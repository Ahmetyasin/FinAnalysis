import pandas as pd
import numpy as np
import json
import os


def narrow_sektor_names(sektor):
    """Classify sectors into broader categories."""
    categories = {
        "imalat": [
            "ambalaj",
            "camseramik",
            "kagit",
            "metalesya",
            "mobilya",
            "otomotiv",
            "otoyan",
        ],
        "hizmet": ["destek", "turizm", "ulastirma", "spor"],
        "yatirim": ["gsyo", "menkul", "holding"],
        "Bilisim": ["haberlesme"],
        "kimya": ["ilac"],
        "anametal": ["maden"],
        "gida": ["tarim"],
        "insaat": ["tas"],
    }
    for category, sectors in categories.items():
        if sektor in sectors:
            return category
    return sektor


def preprocess_data(df, fields):
    """Preprocess the dataframe for specific fields."""
    dfx = df[df["donem"] == df["donem"].max()][fields].copy()
    dfx.dropna(inplace=True)
    return dfx


def forming_dict(df, qt=0.9):
    """Form dictionaries for boundaries and ideal values."""
    ideal_values_dict = {}
    quantile_boundaries_dict = {}
    sec_list = list(df["sektor"].unique())

    for i in sec_list:
        dff = df[df.sektor == i].drop("sektor", axis=1, inplace=False).copy()
        valids = dff.le(dff.quantile(qt)).all(axis=1)
        dff = dff[valids]

        ideal_values = dff.mean().to_list()
        sector_name = i.lower()
        ideal_values_dict["ideal_values_" + str(sector_name)] = ideal_values

        dff["Distance"] = np.sqrt(((dff - ideal_values) ** 2).sum(axis=1))
        n_clusters = 10
        dff["Cluster"] = pd.cut(
            dff["Distance"], bins=n_clusters, labels=range(n_clusters, 0, -1)
        )
        dff.sort_values(by="Distance", inplace=True)
        quantile_boundaries = (
            dff["Distance"].quantile(np.linspace(0, 1, n_clusters)).tolist()
        )
        quantile_boundaries_dict["quantile_boundaries_" + str(sector_name)] = (
            quantile_boundaries
        )

    return ideal_values_dict, quantile_boundaries_dict


def save_to_json(data, filename):
    """Save dictionary data to a JSON file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def main():
    current_directory = os.getcwd()
    # Go up one level to the 'FinAnalysis' folder and then into the 'data' folder
    file_path = os.path.join(current_directory, "data", "2022_all_data.csv")

    # Normalize the file path to resolve any symbolic links
    file_path = os.path.normpath(file_path)

    # Read the data
    df = pd.read_csv(file_path)
    df1 = df.copy()
    df1["sektor"] = df1["sektor"].apply(narrow_sektor_names)

    # Get the current directory (which is assumed to be 'src')
    current_directory = os.getcwd()

    # Construct the file path to the 'dicts' directory, which is two levels up, then down into 'data' and 'dicts'
    dicts_directory_path = os.path.join(current_directory, "data", "dicts")

    # Normalize the directory path
    dicts_directory_path = os.path.normpath(dicts_directory_path)

    # Process the data
    # Include your specific processing here using preprocess_data and forming_dict functions
    # Example (you should modify this with your actual fields and processing logic):

    df1["B_1_Donem_Kari"] = df1["69_DONEM_KARI__ZARARI_"]
    df1["B_2_Donem_Satislari"] = df1["60_Satis_Gelirleri"]
    df1["B_3_Toplam_Borc_Buyuklugu"] = (
        df1["3_Kisa_Vadeli_Yukumlulukler"] + df1["4_Uzun_Vadeli_Yukumlulukler"]
    )
    df1["B_4_Toplam_Alacak_Buyuklugu"] = (
            df1["12_Ticari_Alacaklar"]+ df1["13_Diger_Alacaklar"] + df1["23_Diger_Alacaklar"]
        )
    df1["B_5_Aktif_Buyukluk"] = df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"]
    df1["B_6_Ozsermaye_Buyukluk"] = df1["5_Ozkaynaklar"]
    df1["B_7_Isletme_Sermaye_Buyukluk"] = (
        df1["1_Donen_Varliklar"]
        + df1["2_Duran_Varliklar"]
        - (df1["3_Kisa_Vadeli_Yukumlulukler"])
    )
    df1["B_8_Odenmis_Sermaye_Buyukluk"] = (
        df1["1_Donen_Varliklar"]
        + df1["2_Duran_Varliklar"]
        - (df1["3_Kisa_Vadeli_Yukumlulukler"])
        - (df1["4_Uzun_Vadeli_Yukumlulukler"])
    )

    df1["Ortalama_Stoklar"] = df1.groupby("firma", group_keys=False)[
        "15_Stoklar"
    ].apply(lambda x: (x + x.shift(1)) / 2)
    df1["Donem_Basi_Stok"] = df1.groupby("firma", group_keys=False)["15_Stoklar"].apply(
        lambda x: x.shift(1)
    )
    df1["Donem_Basi_Borc"] = (
        df.groupby("firma", group_keys=False)
        .apply(
            lambda x: x["3_Kisa_Vadeli_Yukumlulukler"].shift(1)
            + x["4_Uzun_Vadeli_Yukumlulukler"].shift(1)
        )
        .reset_index(level=0, drop=True)
    )

    mag_fields = [
        "sektor",
        "B_1_Donem_Kari",
        "B_2_Donem_Satislari",
        "B_3_Toplam_Borc_Buyuklugu",
        "B_4_Toplam_Alacak_Buyuklugu",
        "B_5_Aktif_Buyukluk",
        "B_6_Ozsermaye_Buyukluk",
        "B_7_Isletme_Sermaye_Buyukluk",
        "B_8_Odenmis_Sermaye_Buyukluk",
    ]

    mag_df = preprocess_data(df1, mag_fields)
    ideal_values_dict_mag, quantile_boundaries_dict_mag = forming_dict(mag_df, qt=0.9)

    # Save the results
    save_to_json(
        ideal_values_dict_mag,
        os.path.join(dicts_directory_path, "ideal_values_dict_buyukluk.json"),
    )
    save_to_json(
        quantile_boundaries_dict_mag,
        os.path.join(dicts_directory_path, "quantile_boundaries_dict_buyukluk.json"),
    )

    df1["15_Stoklar"].fillna(0, inplace=True)
    df1["18_Pesin_Odenmis_Giderler"].fillna(0, inplace=True)
    df1["10_Nakit_ve_Nakit_Benzerleri"].fillna(0, inplace=True)
    df1["60_Satis_Gelirleri"].fillna(0, inplace=True)
    df1["62_Satislarin_Maliyeti__e_"].fillna(0, inplace=True)
    df1["63_Genel_Yonetim_Giderleri__e_"].fillna(0, inplace=True)
    df1["796_Amortisman"].fillna(0, inplace=True)


    df1["L1_CariOran"] = (df1["1_Donen_Varliklar"]) / (
        df1["3_Kisa_Vadeli_Yukumlulukler"]
    )
    df1["L2_AsitOran"] = (
        df1["1_Donen_Varliklar"] - df1["15_Stoklar"] - df1["18_Pesin_Odenmis_Giderler"]
    ) / (df1["3_Kisa_Vadeli_Yukumlulukler"])
    df1["L3_NakitOran"] = (df1["10_Nakit_ve_Nakit_Benzerleri"]) / (
        df1["3_Kisa_Vadeli_Yukumlulukler"]
    )
    df1["L5_Favok"] = (df1["60_Satis_Gelirleri"]) + (df1["62_Satislarin_Maliyeti__e_"]) + (df1["63_Genel_Yonetim_Giderleri__e_"]) + (df["796_Amortisman"])
    
    liq_fields = ["sektor", "L1_CariOran", "L2_AsitOran", "L3_NakitOran","L5_Favok"]
    liq_df = preprocess_data(df1, liq_fields)
    ideal_values_dict_liq, quantile_boundaries_dict_liq = forming_dict(liq_df, qt=0.9)
    save_to_json(
        ideal_values_dict_liq,
        os.path.join(dicts_directory_path, "ideal_values_dict_likidite.json"),
    )
    save_to_json(
        quantile_boundaries_dict_liq,
        os.path.join(dicts_directory_path, "quantile_boundaries_dict_likidite.json"),
    )

    df1["F1_Finansal_Kaldirac_Orani"] = (
        df1["3_Kisa_Vadeli_Yukumlulukler"] + df1["4_Uzun_Vadeli_Yukumlulukler"]
    ) / (df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"])
    df1["F2_Ozkaynak_Oran"] = (df1["5_Ozkaynaklar"]) / (
        df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"]
    )
    df1["F3_Finansman_Oran"] = (df1["5_Ozkaynaklar"]) / (
        df1["3_Kisa_Vadeli_Yukumlulukler"] + df1["4_Uzun_Vadeli_Yukumlulukler"]
    )
    df1["F4_Sermaye_Carpani"] = (
        df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"]
    ) / (df1["5_Ozkaynaklar"])

    fin_fields = [
        "sektor",
        "F1_Finansal_Kaldirac_Orani",
        "F2_Ozkaynak_Oran",
        "F3_Finansman_Oran",
        "F4_Sermaye_Carpani",
    ]
    fin_df = preprocess_data(df1, fin_fields)
    ideal_values_dict_fin, quantile_boundaries_dict_fin = forming_dict(fin_df, qt=0.9)
    save_to_json(
        ideal_values_dict_fin,
        os.path.join(dicts_directory_path, "ideal_values_dict_finansal_yapi.json"),
    )
    save_to_json(
        quantile_boundaries_dict_fin,
        os.path.join(
            dicts_directory_path, "quantile_boundaries_dict_finansal_yapi.json"
        ),
    )

    df1["V1_Stok_Devir_Hizi"] = (-df1["62_Satislarin_Maliyeti__e_"]) / (
        df1["Ortalama_Stoklar"]
    )
    df1["V3_Alacak_Devir_Hizi"] = (df1["60_Satis_Gelirleri"]) / df1[
        "12_Ticari_Alacaklar"
    ]
    df1["V8_Aktif_Devir_Hizi"] = (df1["60_Satis_Gelirleri"]) / (
        df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"]
    )
    df1["V11_Calisma_Sermayesi_Devir_Hizi"] = (df1["60_Satis_Gelirleri"]) / (
        df1["1_Donen_Varliklar"] - df1["3_Kisa_Vadeli_Yukumlulukler"]
    )

    eff_fields = [
        "sektor",
        "V1_Stok_Devir_Hizi",
        "V3_Alacak_Devir_Hizi",
        "V8_Aktif_Devir_Hizi",
        "V11_Calisma_Sermayesi_Devir_Hizi",
    ]
    eff_df = preprocess_data(df1, eff_fields)
    ideal_values_dict_eff, quantile_boundaries_dict_eff = forming_dict(eff_df, qt=0.8)
    save_to_json(
        ideal_values_dict_eff,
        os.path.join(dicts_directory_path, "ideal_values_dict_varlik_yonetim.json"),
    )
    save_to_json(
        quantile_boundaries_dict_eff,
        os.path.join(
            dicts_directory_path, "quantile_boundaries_dict_varlik_yonetim.json"
        ),
    )

    df1["K1_Ozkaynak_Karlilik"] = (df1["69_DONEM_KARI__ZARARI_"]) / df1["5_Ozkaynaklar"]
    df1["K2_Sermaye_Karlilik"] = (df1["69_DONEM_KARI__ZARARI_"]) / (df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"] - df1["3_Kisa_Vadeli_Yukumlulukler"] - df1["4_Uzun_Vadeli_Yukumlulukler"])
    df1["K3_Aktif_Karlilik"] = (df1["69_DONEM_KARI__ZARARI_"]) / (
        df1["1_Donen_Varliklar"] + df1["2_Duran_Varliklar"]
    )
    df1["K5_Calisma_Sermayesi_Karlilik"] = (df1["69_DONEM_KARI__ZARARI_"]) / (
        df1["1_Donen_Varliklar"] - df1["3_Kisa_Vadeli_Yukumlulukler"]
    )

    prof_fields = [
        "sektor",
        "K1_Ozkaynak_Karlilik",
        "K2_Sermaye_Karlilik",
        "K3_Aktif_Karlilik",
        "K5_Calisma_Sermayesi_Karlilik"
    ]
    prof_df = preprocess_data(df1, prof_fields)
    ideal_values_dict_prof, quantile_boundaries_dict_prof = forming_dict(
        prof_df, qt=0.95
    )

    # Now use this path to save your JSON files
    save_to_json(
        ideal_values_dict_prof,
        os.path.join(dicts_directory_path, "ideal_values_dict_karlilik.json"),
    )
    save_to_json(
        quantile_boundaries_dict_prof,
        os.path.join(dicts_directory_path, "quantile_boundaries_dict_karlilik.json"),
    )


if __name__ == "__main__":
    main()
