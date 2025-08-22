import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gio, Gtk, GLib
import os

class SaveProjectsDialog:
    def __init__(self):
        self.output_folder = os.path.expanduser("~/Desktop")
        self.result = False
        self.overwrite_existing = True
        
    def show_dialog(self):
        """Mostra diálogo de configuração para salvar projetos"""
        # Cria janela principal
        dialog = Gtk.Dialog(
            title="Salvar Todos os Projetos Abertos",
            parent=None
        )
        dialog.set_default_size(450, 250)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Salvar Projetos", Gtk.ResponseType.OK
        )
        
        # Container principal
        vbox = Gtk.VBox(spacing=15)
        vbox.set_border_width(15)
        dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Título explicativo
        title_label = Gtk.Label()
        title_label.set_markup("<b>Salvar projetos no formato XCF do GIMP</b>")
        title_label.set_halign(Gtk.Align.START)
        vbox.pack_start(title_label, False, False, 0)
        
        desc_label = Gtk.Label(
            label="Os projetos serão salvos em formato .xcf preservando todas as camadas,\nefeitos e configurações para edição posterior."
        )
        desc_label.set_halign(Gtk.Align.START)
        vbox.pack_start(desc_label, False, False, 0)
        
        # Separador
        separator = Gtk.HSeparator()
        vbox.pack_start(separator, False, False, 0)
        
        # Seção: Pasta de saída
        folder_frame = Gtk.Frame(label="Pasta de Saída")
        folder_vbox = Gtk.VBox(spacing=8)
        folder_vbox.set_border_width(12)
        folder_frame.add(folder_vbox)
        
        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_text(self.output_folder)
        folder_hbox = Gtk.HBox(spacing=8)
        folder_hbox.pack_start(self.folder_entry, True, True, 0)
        
        folder_button = Gtk.Button(label="Procurar...")
        folder_button.connect("clicked", self.on_folder_button_clicked)
        folder_hbox.pack_start(folder_button, False, False, 0)
        
        folder_vbox.pack_start(folder_hbox, False, False, 0)
        vbox.pack_start(folder_frame, False, False, 0)
        
        # Seção: Opções
        options_frame = Gtk.Frame(label="Opções")
        options_vbox = Gtk.VBox(spacing=8)
        options_vbox.set_border_width(12)
        options_frame.add(options_vbox)
        
        # Checkbox para sobrescrever
        self.overwrite_check = Gtk.CheckButton(label="Sobrescrever arquivos existentes")
        self.overwrite_check.set_active(self.overwrite_existing)
        options_vbox.pack_start(self.overwrite_check, False, False, 0)
        
        # Checkbox para limpar flag "modificado"
        self.mark_clean_check = Gtk.CheckButton(label="Marcar projetos como salvos (remove o '*' do título)")
        self.mark_clean_check.set_active(True)
        options_vbox.pack_start(self.mark_clean_check, False, False, 0)
        
        vbox.pack_start(options_frame, False, False, 0)
        
        dialog.show_all()
        
        # Executa diálogo
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.output_folder = self.folder_entry.get_text()
            self.overwrite_existing = self.overwrite_check.get_active()
            self.mark_clean = self.mark_clean_check.get_active()
            self.result = True
        
        dialog.destroy()
        return self.result
    
    def on_folder_button_clicked(self, button):
        """Abre diálogo de seleção de pasta"""
        dialog = Gtk.FileChooserDialog(
            title="Escolher Pasta para Salvar Projetos",
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

class ProgressDialog:
    def __init__(self, total_projects):
        self.total_projects = total_projects
        self.current = 0
        
        # Cria janela de progresso
        self.dialog = Gtk.Dialog(
            title="Salvando Projetos...",
            parent=None,
            modal=True
        )
        self.dialog.set_default_size(400, 150)
        self.dialog.set_deletable(False)  # Não permite fechar
        
        vbox = Gtk.VBox(spacing=10)
        vbox.set_border_width(20)
        self.dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Label de status
        self.status_label = Gtk.Label(label="Preparando para salvar projetos...")
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
        progress = current / self.total_projects
        
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_text(f"{current}/{self.total_projects}")
        
        if filename:
            self.status_label.set_text(f"Salvando: {filename}")
            self.detail_label.set_text(f"Projeto {current} de {self.total_projects}")
        
        # Força atualização da interface
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def close(self):
        """Fecha diálogo de progresso"""
        self.dialog.destroy()

def save_all_open_projects():
    """Função principal para salvar todos os projetos abertos"""
    
    # Verifica se há projetos abertos
    images = Gimp.get_images()
    if not images:
        # Mostra mensagem de erro
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Nenhum projeto aberto!"
        )
        dialog.format_secondary_text("Abra alguns projetos no GIMP antes de executar este script.")
        dialog.run()
        dialog.destroy()
        return
    
    # Mostra diálogo de configuração
    save_dialog = SaveProjectsDialog()
    if not save_dialog.show_dialog():
        return  # Usuário cancelou
    
    # Cria pasta se necessário
    try:
        os.makedirs(save_dialog.output_folder, exist_ok=True)
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
    
    # Processa cada projeto
    saved_count = 0
    errors = []
    skipped_count = 0
    
    for i, img in enumerate(images):
        try:
            # Nome do arquivo
            current_name = img.get_name()
            
            # Se a imagem já tem nome, usa ele (remove extensão se houver)
            if current_name and current_name != "Untitled":
                if "." in current_name:
                    base_name = current_name.rsplit(".", 1)[0]
                else:
                    base_name = current_name
            else:
                # Se não tem nome, cria um baseado no índice
                base_name = f"projeto_{i+1}"
            
            # Garante que termine com .xcf
            output_filename = f"{base_name}.xcf"
            output_path = os.path.join(save_dialog.output_folder, output_filename)
            
            # Verifica se arquivo já existe e se deve sobrescrever
            if os.path.exists(output_path) and not save_dialog.overwrite_existing:
                skipped_count += 1
                continue
            
            # Atualiza progresso
            progress_dialog.update(i + 1, output_filename)
            
            # Cria objeto Gio.File
            output_file = Gio.File.new_for_path(output_path)
            
            # Salva o projeto em XCF
            # Para XCF, podemos usar tanto file_save quanto xcf_save
            Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, output_file, None)
            
            # Marca como limpo (remove o asterisco do título) se solicitado
            if save_dialog.mark_clean:
                img.clean_all()
            
            saved_count += 1
            
        except Exception as e:
            errors.append(f"{img.get_name() or f'Projeto {i+1}'}: {str(e)}")
    
    # Fecha diálogo de progresso
    progress_dialog.close()
    
    # Mostra resultado final
    if errors:
        # Houve erros
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Salvamento concluído com avisos"
        )
        error_text = f"Projetos salvos: {saved_count}\n"
        if skipped_count > 0:
            error_text += f"Projetos ignorados (já existem): {skipped_count}\n"
        error_text += f"Erros: {len(errors)}\n\nDetalhes dos erros:\n" + "\n".join(errors[:3])
        if len(errors) > 3:
            error_text += f"\n... e mais {len(errors) - 3} erros."
        dialog.format_secondary_text(error_text)
    else:
        # Sucesso total
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Projetos salvos com sucesso!"
        )
        success_text = f"Salvos: {saved_count} projetos"
        if skipped_count > 0:
            success_text += f"\nIgnorados (já existem): {skipped_count}"
        success_text += f"\n\nLocal: {save_dialog.output_folder}\nFormato: XCF (preserva todas as camadas e efeitos)"
        dialog.format_secondary_text(success_text)
    
    dialog.run()
    dialog.destroy()

# Execute a função
save_all_open_projects()