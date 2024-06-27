from src.config import Config
from data.data_loader import load_belb_data, preprocess_data, save_processed_data
from models.rag_model import RagModelWrapper

def main():
    print("SUCCESSFULLY IMPORTED ALL PACKAGES")
    # raw_data = load_belb_data(Config.RAW_DATA_PATH)
    # processed_data = preprocess_data(raw_data)
    # save_processed_data(processed_data, Config.PROCESSED_DATA_PATH + 'processed_belb.csv')
    
    # model = RagModelWrapper(Config.MODEL_NAME)
    # model.train(processed_data['text'])

if __name__ == "__main__":
    main()
