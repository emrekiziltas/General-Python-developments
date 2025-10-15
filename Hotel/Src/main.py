from data_loading import load_data, inspect_data, visualize_missing
from tabs import load_tabs
from css import CUSTOM_CSS

def main():
    # Veri yükle
    data = load_data()

    # Veri incele
    inspect_data(data)

    # Eksik verileri görselleştir
     #visualize_missing(data)

    load_tabs()

if __name__ == "__main__":
    main()
