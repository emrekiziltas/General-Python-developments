from data_loading import load_data, inspect_data, visualize_missing


def main():
    # Veri yükle
    data = load_data()

    # Veri incele
    inspect_data(data)

    # Eksik verileri görselleştir
    visualize_missing(data)

if __name__ == "__main__":
    main()
