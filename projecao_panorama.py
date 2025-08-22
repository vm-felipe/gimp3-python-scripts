import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gio, Gtk, GLib
import os

class PanoramaProjectionDialog:
    def __init__(self):
        self.result = False
        self.tilt_value = 90.0
        self.zoom_value = 50.0
        self.sampler_type = 0  # 0=Nenhum, 1=Linear, 2=Cúbico
        
    def show_dialog(self):
        """Mostra diálogo de configuração para projeção em panorama"""
        # Cria janela principal
        dialog = Gtk.Dialog(
            title="Projeção em Panorama - Processamento em Lote",
            parent=None
        )
        dialog.set_default_size(500, 400)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Processar Todas", Gtk.ResponseType.OK
        )
        
        # Container principal
        vbox = Gtk.VBox(spacing=15)
        vbox.set_border_width(15)
        dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Título explicativo
        title_label = Gtk.Label()
        title_label.set_markup("<b>Processamento Automático de Projeção em Panorama</b>")
        title_label.set_halign(Gtk.Align.START)
        vbox.pack_start(title_label, False, False, 0)
        
        # Descrição do processo
        desc_label = Gtk.Label()
        desc_label.set_markup(
            "Para cada imagem aberta, o script irá:\n"
            "• Duplicar a camada ativa\n"
            "• Inserir canal alfa na camada duplicada\n"
            "• Aplicar filtro <i>Projeção em Panorama</i> com:\n"
            "  - Inclinar: 90° / Ampliação: 50% (valores padrão)\n"
            "  - Sampler: Mais próximo\n"
            "  - Aplicação não-destrutiva seguida de merge\n\n"
            "<i>Nota: Ajuste manualmente a visualização para 'Preencher Janela' antes de executar (View → Zoom → Fit Image in Window)</i>"
        )
        desc_label.set_halign(Gtk.Align.START)
        vbox.pack_start(desc_label, False, False, 0)
        
        # Separador
        separator = Gtk.HSeparator()
        vbox.pack_start(separator, False, False, 0)
        
        # Seção: Configurações da Projeção
        config_frame = Gtk.Frame(label="Configurações da Projeção em Panorama")
        config_vbox = Gtk.VBox(spacing=12)
        config_vbox.set_border_width(15)
        config_frame.add(config_vbox)
        
        # Inclinar (Tilt)
        tilt_hbox = Gtk.HBox(spacing=10)
        tilt_label = Gtk.Label(label="Inclinar:")
        tilt_label.set_size_request(100, -1)
        tilt_hbox.pack_start(tilt_label, False, False, 0)
        
        self.tilt_scale = Gtk.HScale()
        self.tilt_scale.set_range(-180, 180)
        self.tilt_scale.set_value(self.tilt_value)
        self.tilt_scale.set_digits(1)
        self.tilt_scale.set_hexpand(True)
        tilt_hbox.pack_start(self.tilt_scale, True, True, 0)
        
        self.tilt_value_label = Gtk.Label(label=f"{self.tilt_value}°")
        self.tilt_scale.connect("value-changed", self.on_tilt_changed)
        tilt_hbox.pack_start(self.tilt_value_label, False, False, 0)
        
        config_vbox.pack_start(tilt_hbox, False, False, 0)
        
        # Ampliação (Zoom)
        zoom_hbox = Gtk.HBox(spacing=10)
        zoom_label = Gtk.Label(label="Ampliação:")
        zoom_label.set_size_request(100, -1)
        zoom_hbox.pack_start(zoom_label, False, False, 0)
        
        self.zoom_scale = Gtk.HScale()
        self.zoom_scale.set_range(0.01, 1000)
        self.zoom_scale.set_value(self.zoom_value)
        self.zoom_scale.set_digits(1)
        self.zoom_scale.set_hexpand(True)
        zoom_hbox.pack_start(self.zoom_scale, True, True, 0)
        
        self.zoom_value_label = Gtk.Label(label=f"{self.zoom_value}%")
        self.zoom_scale.connect("value-changed", self.on_zoom_changed)
        zoom_hbox.pack_start(self.zoom_value_label, False, False, 0)
        
        config_vbox.pack_start(zoom_hbox, False, False, 0)
        
        # Sampler Type (método de reamostragem correto)
        sampler_hbox = Gtk.HBox(spacing=10)
        sampler_label = Gtk.Label(label="Sampler:")
        sampler_label.set_size_request(100, -1)
        sampler_hbox.pack_start(sampler_label, False, False, 0)
        
        self.sampler_combo = Gtk.ComboBoxText()
        self.sampler_combo.append_text("Mais próximo")   # GEGL_SAMPLER_NEAREST
        self.sampler_combo.append_text("Linear")         # GEGL_SAMPLER_LINEAR
        self.sampler_combo.append_text("Cúbico")         # GEGL_SAMPLER_CUBIC
        self.sampler_combo.append_text("NoHalo")         # GEGL_SAMPLER_NOHALO
        self.sampler_combo.append_text("LoHalo")         # GEGL_SAMPLER_LOHALO
        self.sampler_combo.set_active(0)  # Mais próximo por padrão
        sampler_hbox.pack_start(self.sampler_combo, False, False, 0)
        
        config_vbox.pack_start(sampler_hbox, False, False, 0)
        
        vbox.pack_start(config_frame, False, False, 0)
        
        # Seção: Opções do processamento
        processing_frame = Gtk.Frame(label="Opções de Processamento")
        processing_vbox = Gtk.VBox(spacing=8)
        processing_vbox.set_border_width(12)
        processing_frame.add(processing_vbox)
        
        # Checkbox para preservar imagem original
        self.preserve_original_check = Gtk.CheckButton(label="Preservar camada original (duplicar antes de aplicar)")
        self.preserve_original_check.set_active(True)
        processing_vbox.pack_start(self.preserve_original_check, False, False, 0)
        
        # Tipo de aplicação do filtro
        self.merge_filter_check = Gtk.CheckButton(label="Aplicar destrutivamente (merge imediato)")
        self.merge_filter_check.set_active(True)
        processing_vbox.pack_start(self.merge_filter_check, False, False, 0)
        
        vbox.pack_start(processing_frame, False, False, 0)
        
        dialog.show_all()
        
        # Executa diálogo
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.tilt_value = self.tilt_scale.get_value()
            self.zoom_value = self.zoom_scale.get_value()
            self.sampler_type = self.sampler_combo.get_active()
            self.preserve_original = self.preserve_original_check.get_active()
            self.merge_filter = self.merge_filter_check.get_active()
            self.result = True
        
        dialog.destroy()
        return self.result
    
    def on_tilt_changed(self, scale):
        """Atualiza label do inclinar"""
        value = scale.get_value()
        self.tilt_value_label.set_text(f"{value:.1f}°")
    
    def on_zoom_changed(self, scale):
        """Atualiza label da ampliação"""
        value = scale.get_value()
        self.zoom_value_label.set_text(f"{value:.1f}%")

class ProgressDialog:
    def __init__(self, total_images):
        self.total_images = total_images
        self.current = 0
        
        # Cria janela de progresso
        self.dialog = Gtk.Dialog(
            title="Processando Projeções em Panorama...",
            parent=None,
            modal=True
        )
        self.dialog.set_default_size(450, 180)
        self.dialog.set_deletable(False)
        
        vbox = Gtk.VBox(spacing=15)
        vbox.set_border_width(20)
        self.dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Label de status
        self.status_label = Gtk.Label(label="Preparando processamento...")
        vbox.pack_start(self.status_label, False, False, 0)
        
        # Barra de progresso
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        vbox.pack_start(self.progress_bar, False, False, 0)
        
        # Label de detalhes
        self.detail_label = Gtk.Label(label="")
        vbox.pack_start(self.detail_label, False, False, 0)
        
        # Label de etapa atual
        self.step_label = Gtk.Label(label="")
        vbox.pack_start(self.step_label, False, False, 0)
        
        self.dialog.show_all()
        
        # Força atualização da interface
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def update(self, current, image_name="", step=""):
        """Atualiza progresso"""
        self.current = current
        progress = current / self.total_images
        
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_text(f"{current}/{self.total_images}")
        
        if image_name:
            self.status_label.set_text(f"Processando: {image_name}")
            self.detail_label.set_text(f"Imagem {current} de {self.total_images}")
        
        if step:
            self.step_label.set_text(f"Etapa: {step}")
        
        # Força atualização da interface
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def close(self):
        """Fecha diálogo de progresso"""
        self.dialog.destroy()

def process_panorama_projection():
    """Função principal para processamento em lote da projeção em panorama"""
    
    # Verifica se há imagens abertas
    images = Gimp.get_images()
    if not images:
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
    config_dialog = PanoramaProjectionDialog()
    if not config_dialog.show_dialog():
        return  # Usuário cancelou
    
    # Mostra diálogo de progresso
    progress_dialog = ProgressDialog(len(images))
    
    # Processa cada imagem
    processed_count = 0
    errors = []
    
    for i, img in enumerate(images):
        try:
            image_name = img.get_name() or f"Imagem {i+1}"
            progress_dialog.update(i + 1, image_name, "Preparando...")
            
            # Etapa 1: Obter drawable ativo usando a API correta do GIMP 3.0
            progress_dialog.update(i + 1, image_name, "Obtendo camada ativa...")
            
            # No GIMP 3.0, usamos get_selected_drawables() ao invés de get_active_layer()
            selected_drawables = img.get_selected_drawables()
            
            if not selected_drawables:
                # Se não há seleção, pega todas as camadas
                layers = img.get_layers()
                if not layers:
                    errors.append(f"{image_name}: Nenhuma camada encontrada")
                    continue
                # Usa a primeira camada como padrão
                active_drawable = layers[0]
            else:
                # Usa o primeiro drawable selecionado
                active_drawable = selected_drawables[0]
            
            # Verifica se é uma camada (não canal ou máscara)
            if not isinstance(active_drawable, Gimp.Layer):
                errors.append(f"{image_name}: Drawable selecionado não é uma camada")
                continue
            
            # Etapa 2: Duplicar a camada ativa
            progress_dialog.update(i + 1, image_name, "Duplicando camada...")
            
            # Duplica a camada usando a API correta
            duplicated_layer = active_drawable.copy()
            img.insert_layer(duplicated_layer, None, 0)
            duplicated_layer.set_name(f"{active_drawable.get_name()}_panorama")
            
            # Etapa 3: Inserir canal alfa
            progress_dialog.update(i + 1, image_name, "Adicionando canal alfa...")
            if not duplicated_layer.has_alpha():
                duplicated_layer.add_alpha()
            
            # Etapa 4: Aplicar filtro Projeção em Panorama usando a API oficial do GIMP 3.0
            progress_dialog.update(i + 1, image_name, "Aplicando projeção em panorama...")
            
            try:
                # Mapeamento dos sampler types baseado na documentação GEGL oficial:
                # sampler-type é do tipo enum e espera strings, não números!
                sampler_mapping = ["nearest", "linear", "cubic", "nohalo", "lohalo"]
                sampler_string = sampler_mapping[config_dialog.sampler_type]
                
                # GIMP 3.0: Método oficial da documentação - Usar DrawableFilter
                # Baseado em: https://developer.gimp.org/resource/writing-a-plug-in/tutorial-gegl-ops/
                filter_obj = Gimp.DrawableFilter.new(
                    duplicated_layer, 
                    "gegl:panorama-projection", 
                    "Panorama Projection"
                )
                
                # Configura as propriedades do filtro
                config = filter_obj.get_config()
                
                # Propriedades oficiais do gegl:panorama-projection (documentação GEGL):
                config.set_property('pan', 0.0)                          # Pan: -360 to 360 degrees
                config.set_property('tilt', config_dialog.tilt_value)     # Tilt: -180 to 180 degrees
                config.set_property('spin', 0.0)                         # Spin: -360 to 360 degrees
                config.set_property('zoom', config_dialog.zoom_value)     # Zoom: 0.01 to 1000.0
                config.set_property('sampler-type', sampler_string)       # Sampler type: string enum
                
                # Atualiza o filtro com as configurações
                filter_obj.update()
                
                # Aplica o filtro de acordo com a opção escolhida
                if config_dialog.merge_filter:
                    # Aplica destrutivamente (merge imediato)
                    duplicated_layer.merge_filter(filter_obj)
                else:
                    # Aplica não-destrutivamente (mantém o filtro editável)
                    duplicated_layer.append_filter(filter_obj)
                
                processed_count += 1
                progress_dialog.update(i + 1, image_name, "Concluído!")
                
            except Exception as filter_error:
                errors.append(f"{image_name}: Erro ao aplicar filtro - {str(filter_error)}")
                continue
            
            # Força atualização das visualizações
            Gimp.displays_flush()
            
        except Exception as e:
            errors.append(f"{image_name}: Erro geral - {str(e)}")
    
    # Fecha diálogo de progresso
    progress_dialog.close()
    
    # Mostra resultado final
    if errors:
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Processamento concluído com avisos"
        )
        error_text = f"Processadas: {processed_count}/{len(images)} imagens\n\nErros encontrados:\n"
        error_text += "\n".join(errors[:5])
        if len(errors) > 5:
            error_text += f"\n... e mais {len(errors) - 5} erros."
        dialog.format_secondary_text(error_text)
    else:
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Processamento concluído com sucesso!"
        )
        
        sampler_names = ["Mais próximo", "Linear", "Cúbico", "NoHalo", "LoHalo"]
        dialog.format_secondary_text(
            f"Todas as {processed_count} imagens foram processadas.\n\n"
            f"Configurações aplicadas:\n"
            f"• Pan: 0.0° (fixo)\n"
            f"• Tilt: {config_dialog.tilt_value:.1f}°\n"
            f"• Spin: 0.0° (fixo)\n"
            f"• Zoom: {config_dialog.zoom_value:.1f}\n"
            f"• Sampler: {sampler_names[config_dialog.sampler_type]}\n"
            f"• Aplicação: {'Destrutiva (merge)' if config_dialog.merge_filter else 'Não-destrutiva (editável)'}\n\n"
            f"💡 Dica: Para melhor visualização, use View → Zoom → Fit Image in Window (Shift+Ctrl+J)"
        )
    
    dialog.run()
    dialog.destroy()

# Execute a função
process_panorama_projection()