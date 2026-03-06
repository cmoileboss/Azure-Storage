from pathlib import Path

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, ContentSettings, generate_blob_sas

from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

load_dotenv()

class BlobStorageManager:

    def __init__(self, connection_string=None):
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)


    def get_blob_service(self):
        return self.blob_service


    def get_all_containers(self):
        containers = self.blob_service.list_containers()
        return [container.name for container in containers]


    def create_container(self, container_name: str):
        try:
            self.blob_service.create_container(container_name)
            print(f"Container '{container_name}' créé avec succès.")
        except Exception as e:
            print("Erreur : ", e)


    def delete_container(self, container_name: str):
        try:
            self.blob_service.delete_container(container_name)
            print(f"Container '{container_name}' supprimé avec succès.")
        except Exception as e:
            print("Erreur : ", e)


    def upload_folder(self, container_name: str, folder_path: str):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)
                self.upload_file(container_name=container_name, file_path=file_path, blob_name=file_path)
    
    
    def upload_website(self, folder_path):
        """
        Upload un site web dans le conteneur $web avec les chemins relatifs.
        Les fichiers seront uploadés à la racine ou en conservant la structure interne du dossier.
        """
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculer le chemin relatif par rapport au dossier source
                relative_path = os.path.relpath(file_path, folder_path)
                # Remplacer les backslashes par des slashes pour Azure
                blob_name = relative_path.replace("\\", "/")
                print(f"Upload: {file_path} → $web/{blob_name}")
                self.upload_file(container_name="$web", file_path=file_path, blob_name=blob_name)
    

    def upload_file(self, container_name, file_path: str, blob_name: str):
        try:
            with open(file_path, "rb") as data:
                container = self.blob_service.get_container_client(container_name)
                extention = Path(file_path).suffix
                content_type = None
                if extention == ".html":
                    content_type = "text/html"
                elif extention == ".css":
                    content_type = "text/css"
                
                if content_type is None:
                    container.upload_blob(
                        name = blob_name,
                        data = data,
                        overwrite = True
                    )
                else:
                    content_settings = ContentSettings(content_type=content_type)
                    container.upload_blob(
                        name = blob_name,
                        data = data,
                        overwrite = True,
                        content_settings=content_settings
                    )
        except Exception as e:
            print("Erreur : ", e)


    def upload_data(self, container_name: str, container_file_name: str, content: str):
        try:
            container = self.blob_service.get_container_client(container_name)
            container.upload_blob(
                name = container_file_name,
                data = content,
                overwrite = True)
        except Exception as e:
            print("Erreur : ", e)


    def get_all_blobs_in_container(self, container_name: str):
        try:
            container = self.blob_service.get_container_client(container_name)
            blobs = container.list_blobs()
            return [blob.name for blob in blobs]
        except Exception as e:
            print("Erreur : ", e)
            return []


    def download_blob(self, container_name: str, blob_name: str, download_path: str):
        try:
            container = self.blob_service.get_container_client(container_name)
            blob_client = container.get_blob_client(blob_name)
            with open(download_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
        except Exception as e:
            print("Erreur : ", e)


    def delete_blob(self, container_name: str, blob_name: str):
        try:
            container = self.blob_service.get_container_client(container_name)
            blob_client = container.get_blob_client(blob_name)
            blob_client.delete_blob()
            print(f"Blob '{blob_name}' supprimé avec succès du container '{container_name}'.")
        except Exception as e:
            print("Erreur : ", e)


    def generate_temp_url(self, wanted_container_name: str, wanted_blob_name: str):
        try:
            wanted_account_key = self.blob_service.credential.account_key
            
            # Déterminer le type de contenu en fonction de l'extension du fichier
            import mimetypes
            content_type, _ = mimetypes.guess_type(wanted_blob_name)
            
            token = generate_blob_sas(
                account_name = self.blob_service.account_name,
                container_name = wanted_container_name,
                blob_name = wanted_blob_name,
                account_key = wanted_account_key,
                permission = BlobSasPermissions(read=True),
                expiry = datetime.utcnow() + timedelta(hours=1000),
                cache_control = "no-cache",
                content_disposition = "inline",
                content_type = content_type
            )
            
            temp_url = f"https://{self.blob_service.account_name}.blob.core.windows.net/{wanted_container_name}/{wanted_blob_name}?{token}"
            return temp_url
        except Exception as e:
            print("Erreur : ", e)

        


# Exemple d'utilisation
connection_string = "DefaultEndpointsProtocol=https;AccountName=fmstockage;AccountKey=A/aCLa7N4gMcmIeAZqjUci/wmur244f4ZsyQNWaPH3mhW8s29Snhbh68yjzfIsizt3xOkCN+N1Fn+AStQBrn+g==;EndpointSuffix=core.windows.net"
blob_storage_manager = BlobStorageManager(connection_string)
# blob_storage_manager.upload_file("requirements.txt", "test.txt")
# blob_storage_manager.upload_data("test_uploaddata.txt", "Ceci est un test.")


# Upload du site web avec les chemins relatifs corrects
print("📤 Upload du site web dans $web...")
blob_storage_manager.upload_website("portfolio")


temp_html_url = blob_storage_manager.generate_temp_url("$web", "presentation.html")
temp_css_url = blob_storage_manager.generate_temp_url("$web", "presentation.css")
print("html url : ", temp_html_url)
print("css url : ", temp_css_url)