import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gio, Gtk, GLib
import os

class ExportDialog:
    def __init__(self):
        self.output_folder = os.path.expanduser("~/Desktop")
        self.file_extension = "png"
        self.quality = 90
        self.result = False
        
    def show_dialog(self):
        """Mostra diálogo de configuração"""
        # Cria janela principal
        dialog = Gtk.Dialog(
            title="Exportar Todas as Imagens Abertas",
            parent=None
        )
        dialog.set_default_size(400, 300)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Exportar", Gtk.ResponseType.OK
        )
        
        # Container principal
        vbox = Gtk.VBox(spacing=10)
        vbox.set_border_width(10)
        dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Seção: Pasta de saída
        folder_frame = Gtk.Frame(label="Pasta de Saída")
        folder_vbox = Gtk.VBox(spacing=5)
        folder_vbox.set_border_width(10)
        folder_frame.add(folder_vbox)
        
        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_text(self.output_folder)
        folder_hbox = Gtk.HBox(spacing=5)
        folder_hbox.pack_start(self.folder_entry, True, True, 0)
        
        folder_button = Gtk.Button(label="Procurar...")
        folder_button.connect("clicked", self.on_folder_button_clicked)
        folder_hbox.pack_start(folder_button, False, False, 0)
        
        folder_vbox.pack_start(folder_hbox, False, False, 0)
        vbox.pack_start(folder_frame, False, False, 0)
        
        # Seção: Formato
        format_frame = Gtk.Frame(label="Formato de Exportação")
        format_vbox = Gtk.VBox(spacing=5)
        format_vbox.set_border_width(10)
        format_frame.add(format_vbox)
        
        # Radio buttons para formato
        self.png_radio = Gtk.RadioButton.new_with_label_from_widget(None, "PNG (sem perda)")
        self.jpg_radio = Gtk.RadioButton.new_with_label_from_widget(self.png_radio, "JPEG (menor tamanho)")
        self.bmp_radio = Gtk.RadioButton.new_with_label_from_widget(self.png_radio, "BMP (sem compressão)")
        self.tiff_radio = Gtk.RadioButton.new_with_label_from_widget(self.png_radio, "TIFF (alta qualidade)")
        
        format_vbox.pack_start(self.png_radio, False, False, 0)
        format_vbox.pack_start(self.jpg_radio, False, False, 0)
        format_vbox.pack_start(self.bmp_radio, False, False, 0)
        format_vbox.pack_start(self.tiff_radio, False, False, 0)
        
        # Conecta eventos para mostrar/ocultar controle de qualidade
        self.jpg_radio.connect("toggled", self.on_format_changed)
        self.png_radio.connect("toggled", self.on_format_changed)
        
        vbox.pack_start(format_frame, False, False, 0)
        
        # Seção: Qualidade (inicialmente oculta)
        self.quality_frame = Gtk.Frame(label="Qualidade")
        quality_vbox = Gtk.VBox(spacing=5)
        quality_vbox.set_border_width(10)
        self.quality_frame.add(quality_vbox)
        
        # Slider de qualidade
        quality_hbox = Gtk.HBox(spacing=10)
        quality_label = Gtk.Label(label="Qualidade:")
        quality_hbox.pack_start(quality_label, False, False, 0)
        
        self.quality_scale = Gtk.HScale()
        self.quality_scale.set_range(10, 100)
        self.quality_scale.set_value(self.quality)
        self.quality_scale.set_digits(0)
        self.quality_scale.set_hexpand(True)
        quality_hbox.pack_start(self.quality_scale, True, True, 0)
        
        self.quality_value_label = Gtk.Label(label=f"{self.quality}%")
        self.quality_scale.connect("value-changed", self.on_quality_changed)
        quality_hbox.pack_start(self.quality_value_label, False, False, 0)
        
        quality_vbox.pack_start(quality_hbox, False, False, 0)
        vbox.pack_start(self.quality_frame, False, False, 0)
        
        # Inicialmente oculta a seção de qualidade
        self.quality_frame.set_visible(False)
        
        dialog.show_all()
        
        # Executa diálogo
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.output_folder = self.folder_entry.get_text()
            self.quality = int(self.quality_scale.get_value())
            
            # Determina formato selecionado
            if self.jpg_radio.get_active():
                self.file_extension = "jpg"
            elif self.bmp_radio.get_active():
                self.file_extension = "bmp"
            elif self.tiff_radio.get_active():
                self.file_extension = "tiff"
            else:
                self.file_extension = "png"
            
            self.result = True
        
        dialog.destroy()
        return self.result
    
    def on_folder_button_clicked(self, button):
        """Abre diálogo de seleção de pasta"""
        dialog = Gtk.FileChooserDialog(
            title="Escolher Pasta de Saída",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        dialog.set_current_folder(self.folder_entry.get_text())
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            self.folder_entry.set_text(folder)
        
        dialog.destroy()
    
    def on_format_changed(self, radio_button):
        """Mostra/oculta controle de qualidade baseado no formato"""
        if self.jpg_radio.get_active():
            self.quality_frame.set_visible(True)
        else:
            self.quality_frame.set_visible(False)
    
    def on_quality_changed(self, scale):
        """Atualiza label da qualidade"""
        value = int(scale.get_value())
        self.quality_value_label.set_text(f"{value}%")

class ProgressDialog:
    def __init__(self, total_images):
        self.total_images = total_images
        self.current = 0
        
        # Cria janela de progresso
        self.dialog = Gtk.Dialog(
            title="Exportando Imagens...",
            parent=None,
            modal=True
        )
        self.dialog.set_default_size(400, 150)
        self.dialog.set_deletable(False)  # Não permite fechar
        
        vbox = Gtk.VBox(spacing=10)
        vbox.set_border_width(20)
        self.dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Label de status
        self.status_label = Gtk.Label(label="Preparando exportação...")
        vbox.pack_start(self.status_label, False, False, 0)
        
        # Barra de progresso
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        vbox.pack_start(self.progress_bar, False, False, 0)
        
        # Label de detalhes
        self.detail_label = Gtk.Label(label="")
        vbox.pack_start(self.detail_label, False, False, 0)
        
        self.dialog.show_all()
        
        # Força atualização da interface
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def update(self, current, filename=""):
        """Atualiza progresso"""
        self.current = current
        progress = current / self.total_images
        
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_text(f"{current}/{self.total_images}")
        
        if filename:
            self.status_label.set_text(f"Exportando: {filename}")
            self.detail_label.set_text(f"Arquivo {current} de {self.total_images}")
        
        # Força atualização da interface
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def close(self):
        """Fecha diálogo de progresso"""
        self.dialog.destroy()

def export_all_open_images_with_dialog():
    """Função principal com interface gráfica"""
    
    # Verifica se há imagens abertas
    images = Gimp.get_images()
    if not images:
        # Mostra mensagem de erro
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Nenhuma imagem aberta!"
        )
        dialog.format_secondary_text("Abra algumas imagens no GIMP antes de executar este script.")
        dialog.run()
        dialog.destroy()
        return
    
    # Mostra diálogo de configuração
    export_dialog = ExportDialog()
    if not export_dialog.show_dialog():
        return  # Usuário cancelou
    
    # Cria pasta se necessário
    try:
        os.makedirs(export_dialog.output_folder, exist_ok=True)
    except Exception as e:
        # Mostra erro
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Erro ao criar pasta!"
        )
        dialog.format_secondary_text(f"Não foi possível criar a pasta:\n{str(e)}")
        dialog.run()
        dialog.destroy()
        return
    
    # Mostra diálogo de progresso
    progress_dialog = ProgressDialog(len(images))
    
    # Processa cada imagem
    exported_count = 0
    errors = []
    
    for i, img in enumerate(images):
        try:
            # Nome do arquivo
            base_name = img.get_name() or f"imagem_{i+1}"
            if "." in base_name:
                base_name = base_name.rsplit(".", 1)[0]
            
            output_filename = f"{base_name}.{export_dialog.file_extension}"
            output_path = os.path.join(export_dialog.output_folder, output_filename)
            
            # Atualiza progresso
            progress_dialog.update(i + 1, output_filename)
            
            # Cria objeto Gio.File
            output_file = Gio.File.new_for_path(output_path)
            
            # Exporta usando Gimp.file_save
            Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, output_file, None)
            
            exported_count += 1
            
        except Exception as e:
            errors.append(f"{img.get_name()}: {str(e)}")
    
    # Fecha diálogo de progresso
    progress_dialog.close()
    
    # Mostra resultado final
    if errors:
        # Houve erros
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=f"Exportação concluída com avisos"
        )
        error_text = f"Exportadas: {exported_count}/{len(images)} imagens.\n\nErros:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            error_text += f"\n... e mais {len(errors) - 5} erros."
        dialog.format_secondary_text(error_text)
    else:
        # Sucesso total
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Exportação concluída com sucesso!"
        )
        dialog.format_secondary_text(
            f"Todas as {exported_count} imagens foram exportadas para:\n{export_dialog.output_folder}"
        )
    
    dialog.run()
    dialog.destroy()

# Execute a função
export_all_open_images_with_dialog()