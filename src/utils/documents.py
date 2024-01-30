import os
import pandas as pd

def get_documents(path):
    docs, metas, ids = [], [], []

    if os.path.exists(path):
        i = 0
        df = pd.read_parquet(path)
        df = df.loc[df["organizer_name"] == "Helsingin yliopisto"]
        df = df.sample(n=300).reset_index(drop=True)
        
        for row in df.to_dict("records"):
            code = row["code"]
            study_type = row["study_type"].split(":")[-1]
            organizer_name = row["organizer_name"]
            study_description = row["study_description"]
            study_ingress = row["study_ingress"]
            study_subject = row["study_subject"]
            additional_information = row["additional_information_localization"]
            formal_content = row["formal_content"]
            study_format = row["study_format"]
            formal_description = row["formal_description"]

            if study_type != "peppi":    
                content = f'\tCode:\n\t\t"{code}"\n\tStudy Type:\n\t\t"{study_type}"\n\tOrganizer Name:\n\t\t"{organizer_name}"\n'

                if study_description != "<TYHJÄ>" and study_description  != "Kuvailutietoa ei löytynyt":
                    content += f'\tStudy Description:\n\t\t"{study_description}"\n'

                if study_ingress != "<TYHJÄ>" and study_ingress != "Kuvailutietoa ei löytynyt":
                    content += f'\tStudy Ingress:\n\t\t"{study_ingress}"\n'

                if study_subject != "<TYHJÄ>" and study_subject != "Kuvailutietoa ei löytynyt":
                    content += f'\tStudy Subject:\n\t\t"{study_subject}"\n'

                if additional_information != "<TYHJÄ>" and additional_information != "Kuvailutietoa ei löytynyt":
                    content += f'\tAdditional Information:\n\t\t"{additional_information}"\n'

                if formal_content != "<TYHJÄ>" and formal_content != "Kuvailutietoa ei löytynyt":
                    content += f'\tFormal Content:\n\t\t"{formal_content}"\n'

                if study_format != "<TYHJÄ>" and study_format != "Kuvailutietoa ei löytynyt":
                    content += f'\tStudy Format:\n\t\t"{study_format}"\n'

                if formal_description != "<TYHJÄ>" and formal_description != "Kuvailutietoa ei löytynyt":
                    content += f'\tFormal Description:\n\t\t"{formal_description}"\n'

                for d in [
                    organizer_name,
                    study_description,
                    study_ingress,
                    study_subject,
                    additional_information,
                    formal_content,
                    study_format,
                    formal_description,
                ]:
                    if d != "<TYHJÄ>" and d != "Kuvailutietoa ei löytynyt":
                        ids.append(f"id{i}")
                        metas.append({
                            "code": code,
                            "content": content,
                        })
                        docs.append(d)
                        i += 1

    return docs, metas, ids