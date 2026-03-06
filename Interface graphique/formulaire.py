import random

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QFormLayout, QLineEdit, QPushButton, QLabel, 
                               QTextEdit, QComboBox, QMessageBox, QListWidget, 
                               QHBoxLayout, QListWidgetItem, QScrollArea, QFileDialog, 
                               QInputDialog)
from PySide6.QtCore import Qt, QSize
import sys

from BlobStorageManager import BlobStorageManager


class ContainerItemWidget(QWidget):
    """Widget personnalisé pour afficher un container avec un bouton delete"""
    def __init__(self, container_name, on_delete_clicked_callback):
        super().__init__()
        self.container_name = container_name
        
        # Layout horizontal
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)  # Marges pour donner de l'espace vertical
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Définir une hauteur minimum pour le widget
        self.setMinimumHeight(50)
        
        # Label avec le nom du container
        self.name_label = QLabel(container_name)
        self.name_label.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Espacement
        layout.addStretch()
        
        # Bouton delete
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41408;
            }
        """)
        self.delete_button.clicked.connect(lambda: on_delete_clicked_callback(container_name))
        layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignVCenter)


class BlobItemWidget(QWidget):
    """Widget personnalisé pour afficher un blob avec un bouton delete"""
    def __init__(self, blob_name, on_delete_clicked_callback):
        super().__init__()
        self.blob_name = blob_name
        
        # Layout horizontal
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Définir une hauteur minimum pour le widget
        self.setMinimumHeight(50)
        
        # Label avec le nom du blob
        self.name_label = QLabel(blob_name)
        self.name_label.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Espacement
        layout.addStretch()
        
        # Bouton delete
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41408;
            }
        """)
        self.delete_button.clicked.connect(lambda: on_delete_clicked_callback(blob_name))
        layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignVCenter)


class FormulaireConnectionStringWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formulaire d'upload de données dans Azure Blob Storage")
        self.setGeometry(100, 100, 800, 700)
        
        # Variable pour stocker le container actuellement sélectionné
        self.current_container = None
        
        # Zone de défilement principale
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)
        
        # Widget de contenu
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        content_widget.setLayout(main_layout)
        
        # Titre
        titre = QLabel("Formulaire d'upload de données dans Azure Blob Storage")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titre)
        
        # Formulaire
        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        
        # Champs du formulaire
        self.connection_string_input = QLineEdit()
        self.connection_string_input.setPlaceholderText("Entrez votre chaîne de connexion Azure")
        form_layout.addRow("Chaîne de connexion :", self.connection_string_input)
        
        # Bouton de soumission
        self.submit_button = QPushButton("Se connecter")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.submit_button.clicked.connect(self.on_submit)
        main_layout.addWidget(self.submit_button)
        
        # Bouton de réinitialisation
        self.reset_button = QPushButton("Réinitialiser")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 12px;
                padding: 8px;
                border-radius: 5px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.reset_button.clicked.connect(self.on_reset)
        main_layout.addWidget(self.reset_button)
        
        # Séparateur
        separator = QLabel()
        separator.setStyleSheet("border-top: 2px solid #ccc; margin: 20px 0;")
        main_layout.addWidget(separator)
        
        # Titre de la liste des containers avec bouton +
        containers_header_layout = QHBoxLayout()
        
        self.containers_label = QLabel("Conteneurs disponibles")
        self.containers_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        self.containers_label.setVisible(False)
        containers_header_layout.addWidget(self.containers_label)
        
        # Bouton + pour créer un nouveau container
        self.add_container_button = QPushButton("+")
        self.add_container_button.setFixedSize(30, 30)
        self.add_container_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.add_container_button.clicked.connect(self.on_add_container_clicked)
        self.add_container_button.setVisible(False)
        containers_header_layout.addWidget(self.add_container_button)
        
        containers_header_layout.addStretch()
        main_layout.addLayout(containers_header_layout)
        
        # Liste des containers
        self.containers_list = QListWidget()
        self.containers_list.setMaximumHeight(300)  # Hauteur maximale
        self.containers_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
                min-height: 150px;
                max-height: 300px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        self.containers_list.itemClicked.connect(self.on_container_clicked)
        self.containers_list.setVisible(False)
        main_layout.addWidget(self.containers_list)
        
        # Titre de la liste des blobs avec bouton +
        blobs_header_layout = QHBoxLayout()
        
        self.blobs_label = QLabel("Blobs dans le conteneur")
        self.blobs_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        self.blobs_label.setVisible(False)
        blobs_header_layout.addWidget(self.blobs_label)
        
        # Bouton + pour uploader un nouveau blob
        self.add_blob_button = QPushButton("+")
        self.add_blob_button.setFixedSize(30, 30)
        self.add_blob_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.add_blob_button.clicked.connect(self.on_add_blob_clicked)
        self.add_blob_button.setVisible(False)
        blobs_header_layout.addWidget(self.add_blob_button)
        
        blobs_header_layout.addStretch()
        main_layout.addLayout(blobs_header_layout)
        
        # Liste des blobs
        self.blobs_list = QListWidget()
        self.blobs_list.setMaximumHeight(300)  # Hauteur maximale
        self.blobs_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
                min-height: 150px;
                max-height: 300px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #fff3cd;
            }
            QListWidget::item:selected {
                background-color: #FF9800;
                color: white;
            }
        """)
        self.blobs_list.itemClicked.connect(self.on_blob_clicked)
        self.blobs_list.setVisible(False)
        main_layout.addWidget(self.blobs_list)
        
        # Espacement en bas
        main_layout.addStretch()
    
    def on_submit(self):
        """Fonction appelée lors de la soumission du formulaire"""
        # Récupération des données
        self.connection_string = self.connection_string_input.text().strip()
    
        # Validation simple
        if not self.connection_string:
            QMessageBox.warning(
                self,
                "Champs requis",
                "Veuillez remplir la chaîne de connexion."
            )
            return
        
        try:
            self.blob_storage_manager = BlobStorageManager(self.connection_string)
            self.blob_service = self.blob_storage_manager.get_blob_service()
            
            # Récupération des containers
            containers_list = self.blob_storage_manager.get_all_containers()
            
            # Affichage de la liste des containers avec boutons +
            self.containers_list.clear()
            for container_name in containers_list:
                # Créer un item dans la liste
                item = QListWidgetItem(self.containers_list)
                item.setData(Qt.ItemDataRole.UserRole, container_name)  # Stocker le nom
                
                # Créer le widget personnalisé avec le bouton delete
                container_widget = ContainerItemWidget(container_name, self.on_delete_clicked)
                
                # Définir la taille de l'item avec une hauteur suffisante
                item.setSizeHint(QSize(container_widget.sizeHint().width(), 50))
                
                # Ajouter l'item et le widget
                self.containers_list.addItem(item)
                self.containers_list.setItemWidget(item, container_widget)
            
            # Rendre visible la liste et le label
            self.containers_label.setVisible(True)
            self.containers_list.setVisible(True)
            self.add_container_button.setVisible(True)
            
            # Cacher la liste des blobs
            self.blobs_label.setVisible(False)
            self.blobs_list.setVisible(False)
            self.blobs_list.clear()
            
            # Message de succès
            QMessageBox.information(
                self, 
                "Succès", 
                f"Connexion réussie à Azure Blob Storage !\n{len(containers_list)} conteneur(s) trouvé(s)."
            )
            
            print("\n=== CONNEXION RÉUSSIE ===")
            print(f"Containers trouvés : {containers_list}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de connexion",
                f"Impossible de se connecter à Azure Blob Storage.\n\nErreur : {str(e)}"
            )
            print(f"Erreur : {e}")
    
    def on_reset(self):
        """Réinitialise tous les champs du formulaire"""
        self.connection_string_input.clear()
        self.containers_list.clear()
        self.containers_label.setVisible(False)
        self.containers_list.setVisible(False)
        self.add_container_button.setVisible(False)
        self.blobs_list.clear()
        self.blobs_label.setVisible(False)
        self.blobs_list.setVisible(False)
        self.add_blob_button.setVisible(False)
        print("Formulaire réinitialisé")
    
    def on_container_clicked(self, item):
        """Fonction appelée lors du clic sur un container"""
        container_name = item.data(Qt.ItemDataRole.UserRole)
        print(f"Container sélectionné : {container_name}")
        
        # Stocker le container actuellement sélectionné
        self.current_container = container_name
        
        try:
            # Récupération des blobs du container
            blobs_list = self.blob_storage_manager.get_all_blobs_in_container(container_name)
            
            # Affichage de la liste des blobs
            self.blobs_list.clear()
            
            if blobs_list:
                for blob_name in blobs_list:
                    # Créer un item dans la liste
                    item = QListWidgetItem(self.blobs_list)
                    item.setData(Qt.ItemDataRole.UserRole, blob_name)
                    
                    # Créer le widget personnalisé avec le bouton delete
                    blob_widget = BlobItemWidget(blob_name, self.on_blob_delete_clicked)
                    
                    # Définir la taille de l'item
                    item.setSizeHint(QSize(blob_widget.sizeHint().width(), 50))
                    
                    # Ajouter l'item et le widget
                    self.blobs_list.addItem(item)
                    self.blobs_list.setItemWidget(item, blob_widget)
                
                self.blobs_label.setText(f"Blobs dans '{container_name}' ({len(blobs_list)} blob(s))")
            else:
                self.blobs_list.addItem("Aucun blob trouvé dans ce conteneur")
                self.blobs_label.setText(f"Blobs dans '{container_name}' (vide)")
            
            # Rendre visible la liste des blobs
            self.blobs_label.setVisible(True)
            self.blobs_list.setVisible(True)
            self.add_blob_button.setVisible(True)
            
            print(f"Blobs trouvés : {blobs_list}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de récupérer les blobs du container '{container_name}'.\n\nErreur : {str(e)}"
            )
            print(f"Erreur : {e}")
    
    def on_add_blob_clicked(self):
        """Fonction appelée lors du clic sur le bouton + pour uploader un blob"""
        if not hasattr(self, 'current_container') or not self.current_container:
            QMessageBox.warning(
                self,
                "Aucun conteneur",
                "Veuillez d'abord sélectionner un conteneur."
            )
            return
        
        # Ouvrir le dialogue de sélection de fichier
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier à uploader",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if file_path:
            import os
            blob_name = os.path.basename(file_path)
            
            try:
                # Upload du fichier
                self.blob_storage_manager.upload_file(
                    container_name=self.current_container,
                    file_path=file_path,
                    blob_name=blob_name
                )
                
                QMessageBox.information(
                    self,
                    "Upload réussi",
                    f"Le fichier '{blob_name}' a été uploadé avec succès vers le conteneur '{self.current_container}'."
                )
                
                print(f"Upload réussi : {blob_name} vers {self.current_container}")
                
                # Rafraîchir la liste des blobs
                current_item = self.containers_list.currentItem()
                if current_item:
                    self.on_container_clicked(current_item)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur d'upload",
                    f"Impossible d'uploader le fichier.\n\nErreur : {str(e)}"
                )
                print(f"Erreur d'upload : {e}")
    
    def on_add_container_clicked(self):
        """Fonction appelée lors du clic sur le bouton + pour ajouter un nouveau container"""
        # Demander le nom du nouveau container
        container_name, ok = QInputDialog.getText(
            self,
            "Nouveau conteneur",
            "Entrez le nom du nouveau conteneur :"
        )
        
        if ok and container_name.strip():
            container_name = container_name.strip()
            try:
                self.blob_storage_manager.create_container(container_name)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Le container '{container_name}' a été créé avec succès."
                )
                # Rafraîchir la liste des containers
                self.on_submit()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur de création",
                    f"Impossible de créer le container '{container_name}'.\n\nErreur : {str(e)}"
                )
                print(f"Erreur : {e}")
    
    def on_plus_clicked(self, container_name):
        """Fonction appelée lors du clic sur le bouton + d'un container"""
        print(f"Bouton + cliqué pour le container : {container_name}")
        
        random_number = random.randint(0, 9999)
        self.blob_storage_manager.create_container(container_name + str(random_number))
        # Rafraîchir la liste des containers
        self.on_submit()
    
    def on_delete_clicked(self, container_name):
        """Fonction appelée lors du clic sur le bouton delete d'un container"""
        print(f"Bouton delete cliqué pour le container : {container_name}")
        
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"\u00cates-vous sûr de vouloir supprimer le container '{container_name}' ?\n\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.blob_storage_manager.delete_container(container_name)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Le container '{container_name}' a été supprimé avec succès."
                )
                # Rafraîchir la liste des containers
                self.on_submit()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur de suppression",
                    f"Impossible de supprimer le container '{container_name}'.\n\nErreur : {str(e)}"
                )
                print(f"Erreur : {e}")
    
    def on_blob_delete_clicked(self, blob_name):
        """Fonction appelée lors du clic sur le bouton delete d'un blob"""
        print(f"Bouton delete cliqué pour le blob : {blob_name}")
        
        if not hasattr(self, 'current_container') or not self.current_container:
            QMessageBox.warning(
                self,
                "Erreur",
                "Aucun conteneur sélectionné."
            )
            return
        
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le blob '{blob_name}' du conteneur '{self.current_container}' ?\n\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.blob_storage_manager.delete_blob(self.current_container, blob_name)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Le blob '{blob_name}' a été supprimé avec succès."
                )
                # Rafraîchir la liste des blobs
                # On doit recréer un item factice pour déclencher le refresh
                current_item = self.containers_list.currentItem()
                if current_item:
                    self.on_container_clicked(current_item)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur de suppression",
                    f"Impossible de supprimer le blob '{blob_name}'.\n\nErreur : {str(e)}"
                )
                print(f"Erreur : {e}")
    
    def on_blob_clicked(self, item):
        """Fonction appelée lors du clic sur un blob"""
        blob_name = item.data(Qt.ItemDataRole.UserRole)
        
        if not blob_name or blob_name == "Aucun blob trouvé dans ce conteneur":
            return
        
        print(f"Blob sélectionné : {blob_name}")

        container_name = self.containers_list.currentItem().data(Qt.ItemDataRole.UserRole)
        temp_url = self.blob_storage_manager.generate_temp_url(wanted_container_name = container_name, wanted_blob_name = blob_name)

        # self.blob_storage_manager.download_blob(
        #     container_name = self.containers_list.currentItem().data(Qt.ItemDataRole.UserRole),
        #     blob_name = blob_name,
        #     download_path = f"./{blob_name}"
        # )
        
        # QMessageBox.information(
        #     self,
        #     "Blob sélectionné",
        #     f"Vous avez cliqué sur le blob : {blob_name}\n\nVous avez 5 minutes pour le télécharger à cette url : {temp_url}."
        # )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Blob sélectionné")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(f"Vous avez cliqué sur le blob : {blob_name} du container : {container_name}")
        msg_box.setInformativeText(
            f'Vous avez 5 minutes pour le télécharger à cette url :\n'
            f'<a href="{temp_url}">{temp_url}</a>'
        )
        
        # Activer le format HTML et les interactions
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        
        msg_box.exec()

def main():
    app = QApplication(sys.argv)
    window = FormulaireConnectionStringWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
