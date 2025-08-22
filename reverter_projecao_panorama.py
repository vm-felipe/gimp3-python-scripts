import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gio, Gtk, GLib
import os

class PanoramaInverseDialog:
    def __init__(self):
        self.result = False
        self.tilt_value = 90.0
        self.zoom_value = 50.0
        self.sampler_type = 0  # 0=Mais próximo, 1=Linear, 2=Cúbico, 3=NoHalo, 4=LoHalo
        
    def show_dialog(self):
        """Mostra diálogo de configuração para transformação inversa"""
        # Cria janela principal
        dialog = Gtk.Dialog(
            title="Transformação Inversa - Volta ao Equiretangular",
            parent=None
        )
        dialog.set_default_size(520, 400)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Aplicar Transformação Inversa", Gtk.ResponseType.OK
        )
        
        # Container principal
        vbox = Gtk.VBox(spacing=15)
        vbox.set_border_width(15)
        dialog.get_content_area().pack_start(vbox, True, True, 0)
        
        # Título explicativo
        title_label = Gtk.Label()
        title_label.set_markup("<b>Transformação Inversa - Volta ao Formato Equiretangular</b>")
        title_label.set_halign(Gtk.Align.START)
        vbox.pack_start(title_label, False, False, 0)
        
        # Descrição do processo
        desc_label = Gtk.Label()
        desc_label.set_markup(
            "Este script aplica a <b>transformação inversa</b> de forma simples:\n\n"
            "<b>1º) Transformação Inversa:</b> Aplica na camada ativa/selecionada\n"
            "<b>2º) Combinar Camadas:</b> Usa 'Combinar camadas visíveis' com 'Cortar para camada inferior'\n\n"
            "• <b>Inverse Transform: ATIVADO</b> para voltar ao formato 360°×180°\n"
            "• Usa as mesmas configurações do script de projeção anterior\n\n"
            "<i>💡 Selecione a camada editada antes de executar o script</i>\n"
            "<i>⚠️ Certifique-se de usar as MESMAS configurações (tilt/zoom) do script anterior</i>"
        )
        desc_label.set_halign(Gtk.Align.START)
        vbox.pack_start(desc_label, False, False, 0)
        
        # Separador
        separator = Gtk.HSeparator()
        vbox.pack_start(separator, False, False, 0)
        
        # Seção: Configurações da Transformação Inversa
        config_frame = Gtk.Frame(label="Configurações da Transformação Inversa")
        config_vbox = Gtk.VBox(spacing=12)
        config_vbox.set_border_width(15)
        config_frame.add(config_vbox)
        
        # Aviso importante
        warning_label = Gtk.Label()
        warning_label.set_markup(
            "<b>⚠️ IMPORTANTE:</b> Use as <b>mesmas configurações</b> do script de projeção anterior!"
        )
        warning_label.set_halign(Gtk.Align.START)
        config_vbox.pack_start(warning_label, False, False, 0)
        
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
        
        # Sampler Type (método de reamostragem)
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
        
        # Seção: Processo simplificado
        processing_frame = Gtk.Frame(label="Processo Simplificado")
        processing_vbox = Gtk.VBox(spacing=8)
        processing_vbox.set_border_width(12)
        processing_frame.add(processing_vbox)
        
        # Indicadores do processo
        step1_label = Gtk.Label()
        step1_label.set_markup("<b>1️⃣ Transformação Inversa:</b> Aplicada na camada ativa/selecionada")
        step1_label.set_halign(Gtk.Align.START)
        processing_vbox.pack_start(step1_label, False, False, 0)
        
        step2_label = Gtk.Label()
        step2_label.set_markup("<b>2️⃣ Combinar Camadas:</b> Usando 'Cortar para camada inferior'")
        step2_label.set_halign(Gtk.Align.START)
        processing_vbox.pack_start(step2_label, False, False, 0)
        
        vbox.pack_start(processing_frame, False, False, 0)
        
        dialog.show_all()
        
        # Executa diálogo
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.tilt_value = self.tilt_scale.get_value()
            self.zoom_value = self.zoom_scale.get_value()
            self.sampler_type = self.sampler_combo.get_active()
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

def process_panorama_inverse_transform():
    """Função principal para transformação inversa simplificada"""
    
    # Verifica se há imagens abertas
    images = Gimp.get_images()
    if not images:
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Nenhuma imagem aberta!"
        )
        dialog.format_secondary_text("Abra a imagem editada na vista panorâmica antes de executar este script.")
        dialog.run()
        dialog.destroy()
        return
    
    # Mostra diálogo de configuração
    config_dialog = PanoramaInverseDialog()
    if not config_dialog.show_dialog():
        return  # Usuário cancelou
    
    # Processa cada imagem aberta
    processed_count = 0
    errors = []
    
    for img in images:
        try:
            image_name = img.get_name() or "Imagem sem nome"
            
            # Verifica se há camadas visíveis
            visible_layers = [layer for layer in img.get_layers() if layer.get_visible()]
            if not visible_layers:
                errors.append(f"{image_name}: Nenhuma camada visível encontrada")
                continue
            
            # Obtém a camada ativa (selecionada)
            active_layers = img.get_selected_layers()
            if not active_layers:
                # Se nenhuma camada estiver selecionada, usa a primeira camada visível
                target_layer = visible_layers[0]
            else:
                # Usa a primeira camada selecionada
                target_layer = active_layers[0]
            
            # ETAPA 1: Aplicar transformação inversa na camada alvo
            try:
                # Adiciona canal alfa se não existir
                if not target_layer.has_alpha():
                    target_layer.add_alpha()
                
                # Configura a transformação inversa
                sampler_mapping = ["nearest", "linear", "cubic", "nohalo", "lohalo"]
                sampler_string = sampler_mapping[config_dialog.sampler_type]
                
                # Cria e configura o filtro
                filter_obj = Gimp.DrawableFilter.new(
                    target_layer, 
                    "gegl:panorama-projection", 
                    "Panorama Projection Inverse"
                )
                
                config = filter_obj.get_config()
                config.set_property('pan', 0.0)
                config.set_property('tilt', config_dialog.tilt_value)
                config.set_property('spin', 0.0)
                config.set_property('zoom', config_dialog.zoom_value)
                config.set_property('sampler-type', sampler_string)
                config.set_property('inverse', True)  # TRANSFORMAÇÃO INVERSA ATIVADA!
                
                filter_obj.update()
                
                # Aplica o filtro destrutivamente
                target_layer.merge_filter(filter_obj)
                
            except Exception as transform_error:
                errors.append(f"{image_name}: Erro na transformação inversa - {str(transform_error)}")
                continue
            
            # ETAPA 2: Combinar camadas visíveis com "Cortar para camada inferior"
            try:
                # Verifica novamente as camadas visíveis após a transformação
                visible_layers_after = [layer for layer in img.get_layers() if layer.get_visible()]
                
                if len(visible_layers_after) > 1:
                    # Combina usando CLIP_TO_BOTTOM_LAYER (Cortar para camada inferior)
                    merged_layer = img.merge_visible_layers(Gimp.MergeType.CLIP_TO_BOTTOM_LAYER)
                    merged_layer.set_name("equiretangular_final")
                else:
                    # Se há apenas uma camada visível, apenas renomeia
                    target_layer.set_name("equiretangular_final")
                
                processed_count += 1
                
            except Exception as merge_error:
                errors.append(f"{image_name}: Erro ao combinar camadas - {str(merge_error)}")
                continue
            
            # Força atualização da visualização
            Gimp.displays_flush()
            
        except Exception as e:
            errors.append(f"{image_name}: Erro geral - {str(e)}")
    
    # Mostra resultado final
    if errors:
        dialog = Gtk.MessageDialog(
            parent=None,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Transformação inversa concluída com avisos"
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
            text="Transformação inversa concluída com sucesso!"
        )
        
        sampler_names = ["Mais próximo", "Linear", "Cúbico", "NoHalo", "LoHalo"]
        dialog.format_secondary_text(
            f"Processadas {processed_count} imagens com sucesso.\n\n"
            f"🔄 Configurações aplicadas:\n"
            f"• Tilt: {config_dialog.tilt_value:.1f}°\n"
            f"• Zoom: {config_dialog.zoom_value:.1f}\n"
            f"• Sampler: {sampler_names[config_dialog.sampler_type]}\n"
            f"• Inverse Transform: ATIVADO ✓\n"
            f"• Merge: Cortar para camada inferior ✓\n\n"
            f"✅ PROCESSO SIMPLIFICADO:\n"
            f"1️⃣ Transformação inversa aplicada na camada selecionada\n"
            f"2️⃣ Camadas combinadas com 'Cortar para camada inferior'\n"
            f"✅ Imagem convertida para formato equiretangular (360°×180°)"
        )
    
    dialog.run()
    dialog.destroy()

# Execute a função
process_panorama_inverse_transform()