import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

class QAEModel:
    def __init__(self, model_file: str):
        self.df = pd.read_csv(model_file)

        if 'performance_score' not in self.df.columns:
            raise ValueError("The dataset must contain a 'performance_score' column.")

        self.df['performance_score'].fillna(self.df['performance_score'].mean(), inplace=True)

        self.label_encoder = LabelEncoder()
        self.df['email_encoded'] = self.label_encoder.fit_transform(self.df['email'])

        X = self.df[['experience_years', 'QAE_type', 'feedback', 'pending_request_count']]
        y = self.df['performance_score']

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        self.model = DecisionTreeRegressor(random_state=42)
        self.model.fit(X_train, y_train)

    def select_top_qae(self, new_qaes: pd.DataFrame) -> str:
        new_qaes_scaled = self.scaler.transform(new_qaes[['experience_years', 'QAE_type', 'feedback', 'pending_request_count']])
        predicted_scores = self.model.predict(new_qaes_scaled)
        top_qae_index = predicted_scores.argmax()
        return new_qaes['email'].iloc[top_qae_index]

# Initialize the model (assumes the CSV file is at the specified path)
qae_model = QAEModel('assets/qae_dummy_data.csv')
