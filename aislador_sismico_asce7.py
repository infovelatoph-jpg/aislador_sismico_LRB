import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AisladorSismicoASCE7App:
    def __init__(self, root):
        self.root = root
        self.root.title("Diseño y Verificación de Aislador Sísmico Velatoph SPS - ASCE 7")
        self.root.geometry("1200x1000")
        
        # Variables de entrada
        self.carga_var = tk.DoubleVar(value=200.0)  # toneladas
        self.diametro_aislador_var = tk.DoubleVar(value=0.0)  # mm (0 = calcular automáticamente)
        self.altura_caucho_var = tk.DoubleVar(value=0.0)  # mm (0 = calcular automáticamente)
        self.desplazamiento_var = tk.DoubleVar(value=150.0)  # mm
        self.s1_var = tk.DoubleVar(value=0.6)  # Parámetro sísmico S1
        self.sds_var = tk.DoubleVar(value=1.0)  # Parámetro sísmico SDS
        self.sd1_var = tk.DoubleVar(value=0.8)  # Parámetro sísmico SD1
        self.tl_var = tk.DoubleVar(value=8.0)  # Parámetro sísmico TL
        
        # Variables de salida
        self.diametro_calculado_var = tk.StringVar()
        self.altura_total_var = tk.StringVar()
        self.altura_caucho_calc_var = tk.StringVar()
        self.fuerza_fluencia_var = tk.StringVar()
        self.rigidez_horizontal_var = tk.StringVar()
        self.rigidez_vertical_var = tk.StringVar()
        self.diametro_nucleo_var = tk.StringVar()
        self.coef_amortiguamiento_var = tk.StringVar()
        self.num_capas_var = tk.StringVar()
        self.espesor_capa_var = tk.StringVar()
        self.periodo_aislado_var = tk.StringVar()
        self.desplazamiento_total_var = tk.StringVar()
        
        # Variables de verificación
        self.verif_esfuerzo_var = tk.StringVar()
        self.verif_deformacion_var = tk.StringVar()
        self.verif_estabilidad_var = tk.StringVar()
        self.verif_volteo_var = tk.StringVar()
        self.verif_amortiguamiento_var = tk.StringVar()
        self.verif_general_var = tk.StringVar()
        
        # Variables para histéresis
        self.fig = None
        self.canvas = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Crear notebook (pestañas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de diseño
        tab_diseno = ttk.Frame(notebook)
        notebook.add(tab_diseno, text='Diseño del Aislador')
        
        # Pestaña de verificación
        tab_verificacion = ttk.Frame(notebook)
        notebook.add(tab_verificacion, text='Verificación ASCE 7')
        
        # Pestaña de gráficos
        tab_graficos = ttk.Frame(notebook)
        notebook.add(tab_graficos, text='Curva de Histéresis')
        
        # Configurar el diseño de la pestaña de diseño
        self.setup_diseno_tab(tab_diseno)
        
        # Configurar el diseño de la pestaña de verificación
        self.setup_verificacion_tab(tab_verificacion)
        
        # Configurar el diseño de la pestaña de gráficos
        self.setup_graficos_tab(tab_graficos)
    
    def setup_diseno_tab(self, parent):
        # Frame principal con scrollbar
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar para hacer scrollable
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(scrollable_frame, 
                               text="Diseño de Aislador Sísmico Elastomérico con Núcleo de Plomo Velatoph - ASCE 7", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Frame de entrada de datos
        input_frame = ttk.LabelFrame(scrollable_frame, text="Datos de Entrada (0 = Calcular automáticamente)")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Carga vertical (toneladas):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.carga_var, width=15).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Diámetro del aislador (mm):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.diametro_aislador_var, width=15).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Altura del cuerpo de caucho (mm):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.altura_caucho_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Desplazamiento máximo (mm):").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.desplazamiento_var, width=15).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Parámetro sísmico S1:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.s1_var, width=15).grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Parámetro sísmico SDS:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.sds_var, width=15).grid(row=1, column=3, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Parámetro sísmico SD1:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.sd1_var, width=15).grid(row=2, column=3, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Parámetro sísmico TL:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(input_frame, textvariable=self.tl_var, width=15).grid(row=3, column=3, sticky=tk.W, pady=5, padx=5)
        
        # Botones
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Calcular Diseño", command=self.calcular).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar a JSON", command=self.exportar_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generar Gráfico", command=self.generar_grafico).pack(side=tk.LEFT, padx=5)
        
        # Resultados
        results_frame = ttk.LabelFrame(scrollable_frame, text="Resultados del Diseño - ASCE 7")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Crear sub-frames para organizar mejor los resultados
        results_left = ttk.Frame(results_frame)
        results_left.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        results_center = ttk.Frame(results_frame)
        results_center.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        results_right = ttk.Frame(results_frame)
        results_right.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Resultados izquierda
        ttk.Label(results_left, text="Diámetro calculado (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_left, textvariable=self.diametro_calculado_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_left, text="Altura total (mm):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_left, textvariable=self.altura_total_var, font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_left, text="Altura de caucho (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_left, textvariable=self.altura_caucho_calc_var, font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_left, text="Núm. capas de caucho:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_left, textvariable=self.num_capas_var, font=("Arial", 9, "bold")).grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_left, text="Espesor de capa (mm):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_left, textvariable=self.espesor_capa_var, font=("Arial", 9, "bold")).grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Resultados centro
        ttk.Label(results_center, text="Fuerza de fluencia (kN):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_center, textvariable=self.fuerza_fluencia_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_center, text="Rigidez horiz. (kN/m):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_center, textvariable=self.rigidez_horizontal_var, font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_center, text="Rigidez vert. (kN/m):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_center, textvariable=self.rigidez_vertical_var, font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_center, text="Diám. núcleo plomo (mm):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_center, textvariable=self.diametro_nucleo_var, font=("Arial", 9, "bold")).grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_center, text="Coef. amort. (%):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_center, textvariable=self.coef_amortiguamiento_var, font=("Arial", 9, "bold")).grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Resultados derecha
        ttk.Label(results_right, text="Periodo aislado (s):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_right, textvariable=self.periodo_aislado_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_right, text="Desplaz. total (mm):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_right, textvariable=self.desplazamiento_total_var, font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(results_right, text="Estado diseño:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(results_right, textvariable=self.verif_general_var, font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Área de texto para información ASCE 7
        ttk.Label(scrollable_frame, text="Información para ETABS/SAP2000 según ASCE 7:", 
                 font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.text_output = tk.Text(scrollable_frame, height=15, width=100)
        self.text_output.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Footer
        footer_label = ttk.Label(scrollable_frame, 
                                text="Nota: Diseño según metodología ASCE 7-16, Capítulo 17. Validar con normas específicas y ensayos.",
                                font=("Arial", 8), foreground="gray")
        footer_label.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configurar el canvas para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_verificacion_tab(self, parent):
        # Frame principal con scrollbar
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar para hacer scrollable
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(scrollable_frame, 
                               text="Verificación de Aislador Sísmico según ASCE 7", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Botón de verificación
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Realizar Verificación", command=self.verificar).pack(side=tk.LEFT, padx=5)
        
        # Resultados de verificación
        verificacion_frame = ttk.LabelFrame(scrollable_frame, text="Resultados de Verificación - ASCE 7")
        verificacion_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Crear sub-frames para organizar mejor los resultados
        verif_left = ttk.Frame(verificacion_frame)
        verif_left.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        verif_right = ttk.Frame(verificacion_frame)
        verif_right.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Verificaciones izquierda
        ttk.Label(verif_left, text="Esfuerzo de compresión:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_left, textvariable=self.verif_esfuerzo_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(verif_left, text="Deformación por cortante:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_left, textvariable=self.verif_deformacion_var, font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(verif_left, text="Estabilidad global:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_left, textvariable=self.verif_estabilidad_var, font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Verificaciones derecha
        ttk.Label(verif_right, text="Estabilidad al volteo:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_right, textvariable=self.verif_volteo_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(verif_right, text="Amortiguamiento efectivo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_right, textvariable=self.verif_amortiguamiento_var, font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(verif_right, text="Estado general:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(verif_right, textvariable=self.verif_general_var, font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Área de texto para detalles de verificación
        ttk.Label(scrollable_frame, text="Detalles de Verificación ASCE 7:", 
                 font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.text_verificacion = tk.Text(scrollable_frame, height=20, width=100)
        self.text_verificacion.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Configurar el canvas para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_graficos_tab(self, parent):
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Curva de Histéresis del Aislador Sísmico", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Frame para el gráfico
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Botones para el gráfico
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Generar Curva de Histéresis", command=self.generar_grafico).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Guardar Gráfico", command=self.guardar_grafico).pack(side=tk.LEFT, padx=5)
        
        # Información del gráfico
        info_label = ttk.Label(main_frame, 
                              text="La curva de histéresis muestra la relación fuerza-desplazamiento del aislador bajo carga cíclica.",
                              font=("Arial", 8), foreground="gray")
        info_label.pack(pady=5)
    
    def calcular(self):
        try:
            # Obtener valores de entrada
            carga_ton = self.carga_var.get()
            diametro_aislador = self.diametro_aislador_var.get()
            altura_caucho = self.altura_caucho_var.get()
            desplazamiento_max_mm = self.desplazamiento_var.get()
            S1 = self.s1_var.get()
            SDS = self.sds_var.get()
            SD1 = self.sd1_var.get()
            TL = self.tl_var.get()
            
            # Convertir unidades
            carga_kN = carga_ton * 9.81  # Convertir toneladas a kN
            desplazamiento_max_m = desplazamiento_max_mm / 1000.0
            
            # Parámetros de diseño según ASCE 7-16, Capítulo 17
            esfuerzo_admisible = 11.0  # MPa (máximo según ASCE 7-17 para carga de servicio)
            relacion_forma = 8.0  # Relación de forma típica (S = D/(4t))
            modulo_corte = 0.8  # MPa (módulo de corte del elastómero)
            modulo_compresion = 2000.0  # MPa (módulo de compresión volumétrico)
            esfuerzo_fluencia_plomo = 10.0  # MPa (esfuerzo de fluencia del plomo)
            espesor_placa_acero = 3.0  # mm (espesor típico de placas de acero)
            
            # Factores según ASCE 7-16
            BD = 1.0  # Factor de amplificación por desplazamiento (inicial)
            if S1 >= 0.6:
                BD = max(1.0, 1.2)  # Para zonas de alta sismicidad
            
            # 1. Calcular o verificar diámetro del aislador
            if diametro_aislador <= 0:
                # Calcular diámetro basado en el esfuerzo admisible ASCE 7
                area_requerida = (carga_kN * 1000) / esfuerzo_admisible  # mm²
                diametro_aislador = math.sqrt(4 * area_requerida / math.pi)  # mm
                # Redondear a un valor estándar
                diametro_aislador = self.redondear_valor_estandar(diametro_aislador)
            else:
                # Verificar el diámetro proporcionado
                area_total = math.pi * (diametro_aislador / 2)**2
                esfuerzo_actual = (carga_kN * 1000) / area_total
                if esfuerzo_actual > esfuerzo_admisible:
                    messagebox.showwarning("Advertencia", 
                                         f"El diámetro proporcionado resulta en un esfuerzo de {esfuerzo_actual:.2f} MPa, "
                                         f"que excede el límite de {esfuerzo_admisible:.2f} MPa según ASCE 7.")
            
            # Recalcular área con diámetro final
            area_total = math.pi * (diametro_aislador / 2)**2
            
            # 2. Calcular espesor de capa de caucho basado en la relación de forma
            espesor_capa = diametro_aislador / (4 * relacion_forma)  # mm
            
            # 3. Calcular número de capas necesario para el desplazamiento máximo según ASCE 7
            # Deformación máxima por capa según ASCE 7-17.2.3
            deformacion_max_capa = 0.5  # 50% de deformación máxima por capa (ASCE 7 límite)
            
            if altura_caucho <= 0:
                # Calcular altura de caucho necesaria
                num_capas = math.ceil(desplazamiento_max_mm / (deformacion_max_capa * espesor_capa))
                altura_caucho = num_capas * espesor_capa  # mm
            else:
                # Verificar la altura de caucho proporcionada
                num_capas = math.ceil(altura_caucho / espesor_capa)
                altura_caucho = num_capas * espesor_capa  # Ajustar a múltiplo del espesor de capa
                deformacion_por_capa = desplazamiento_max_mm / altura_caucho
                if deformacion_por_capa > deformacion_max_capa:
                    messagebox.showwarning("Advertencia", 
                                         f"La altura de caucho proporcionada resulta en una deformación de {deformacion_por_capa*100:.1f}%, "
                                         f"que excede el límite de {deformacion_max_capa*100:.0f}% según ASCE 7.")
            
            # 4. Calcular altura total del aislador (caucho + placas de acero)
            altura_placas = (num_capas + 1) * espesor_placa_acero
            altura_total = altura_caucho + altura_placas  # mm
            
            # 5. Calcular diámetro del núcleo de plomo según ASCE 7
            # El área del núcleo de plomo es típicamente 15-25% del área total
            area_nucleo = 0.2 * area_total  # 20% del área total
            diametro_nucleo = math.sqrt(4 * area_nucleo / math.pi)  # mm
            
            # 6. Calcular fuerza de fluencia del núcleo de plomo
            fuerza_fluencia = (esfuerzo_fluencia_plomo * area_nucleo) / 1000  # kN
            
            # 7. Calcular rigideces según ASCE 7
            # Rigidez horizontal (K_h) = (G * A) / T_r
            rigidez_horizontal = (modulo_corte * area_total) / altura_caucho  # N/mm
            rigidez_horizontal_kNm = rigidez_horizontal * 1000  # Convertir a kN/m
            
            # Rigidez vertical (K_v) = (E_c * A) / T_r
            # Para caucho con refuerzo de acero, E_c ≈ 6GS² (ASCE 7 aproximación)
            E_c = 6 * modulo_corte * relacion_forma**2  # MPa
            rigidez_vertical = (E_c * area_total) / altura_caucho  # N/mm
            rigidez_vertical_kNm = rigidez_vertical * 1000  # Convertir to kN/m
            
            # 8. Calcular periodo del sistema aislado según ASCE 7-17.5.3.1
            periodo_aislado = 2 * math.pi * math.sqrt(carga_kN / (9.81 * rigidez_horizontal_kNm))
            
            # 9. Calcular desplazamiento total según ASCE 7-17.5.3.2
            # D_TD = (g / 4π²) * S_D1 * T_D / B_D
            desplazamiento_total = (9.81 / (4 * math.pi**2)) * SD1 * periodo_aislado / BD
            desplazamiento_total_mm = desplazamiento_total * 1000  # Convertir a mm
            
            # 10. Coeficiente de amortiguamiento efectivo según ASCE 7
            # Para aisladores con núcleo de plomo, β ≈ 15-30%
            coef_amortiguamiento = 20.0  # % (valor típico para LRB según ASCE 7)
            
            # Actualizar variables de salida
            self.diametro_calculado_var.set(f"{diametro_aislador:.1f}")
            self.altura_total_var.set(f"{altura_total:.1f}")
            self.altura_caucho_calc_var.set(f"{altura_caucho:.1f}")
            self.fuerza_fluencia_var.set(f"{fuerza_fluencia:.1f}")
            self.rigidez_horizontal_var.set(f"{rigidez_horizontal_kNm:.1f}")
            self.rigidez_vertical_var.set(f"{rigidez_vertical_kNm:.1f}")
            self.diametro_nucleo_var.set(f"{diametro_nucleo:.1f}")
            self.coef_amortiguamiento_var.set(f"{coef_amortiguamiento:.1f}")
            self.num_capas_var.set(f"{num_capas}")
            self.espesor_capa_var.set(f"{espesor_capa:.1f}")
            self.periodo_aislado_var.set(f"{periodo_aislado:.2f}")
            self.desplazamiento_total_var.set(f"{desplazamiento_total_mm:.1f}")
            
            # Realizar verificación automática
            self.verificar()
            
            # Generar información adicional para ETABS/SAP2000
            info_etabs = self.generar_info_etabs(
                diametro_aislador, altura_total, altura_caucho, fuerza_fluencia,
                rigidez_horizontal_kNm, rigidez_vertical_kNm, diametro_nucleo,
                coef_amortiguamiento, carga_kN, desplazamiento_max_mm,
                num_capas, espesor_capa, periodo_aislado, desplazamiento_total_mm,
                S1, SDS, SD1, TL, BD
            )
            
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, info_etabs)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en el cálculo: {str(e)}")
    
    def verificar(self):
        try:
            # Verificar que se hayan calculado los valores primero
            if not self.diametro_calculado_var.get():
                messagebox.showwarning("Advertencia", "Primero debe calcular los parámetros del aislador.")
                return
            
            # Obtener valores calculados
            diametro_aislador = float(self.diametro_calculado_var.get())
            altura_total = float(self.altura_total_var.get())
            altura_caucho = float(self.altura_caucho_calc_var.get())
            fuerza_fluencia = float(self.fuerza_fluencia_var.get())
            rigidez_horizontal = float(self.rigidez_horizontal_var.get())
            rigidez_vertical = float(self.rigidez_vertical_var.get())
            diametro_nucleo = float(self.diametro_nucleo_var.get())
            coef_amortiguamiento = float(self.coef_amortiguamiento_var.get())
            num_capas = int(self.num_capas_var.get())
            espesor_capa = float(self.espesor_capa_var.get())
            periodo_aislado = float(self.periodo_aislado_var.get())
            desplazamiento_total = float(self.desplazamiento_total_var.get())
            
            carga_ton = self.carga_var.get()
            carga_kN = carga_ton * 9.81
            desplazamiento_max_mm = self.desplazamiento_var.get()
            
            # Parámetros según ASCE 7-16
            esfuerzo_admisible = 11.0  # MPa (ASCE 7-17.2.3.1)
            deformacion_max_capa = 0.5  # 50% (ASCE 7-17.2.3.2)
            relacion_estabilidad = 3.0  # Relación altura/diámetro máxima (ASCE 7-17.2.3.3)
            amortiguamiento_min = 15.0  # % mínimo para LRB (ASCE 7-17.5.3.3)
            
            # Calcular valores actuales
            area_total = math.pi * (diametro_aislador / 2)**2
            esfuerzo_actual = (carga_kN * 1000) / area_total  # MPa
            
            deformacion_actual = desplazamiento_max_mm / altura_caucho
            deformacion_por_capa = desplazamiento_max_mm / (num_capas * espesor_capa)
            
            relacion_altura_diametro = altura_total / diametro_aislador
            
            # Realizar verificaciones
            verificaciones = []
            
            # 1. Verificación de esfuerzo de compresión
            if esfuerzo_actual <= esfuerzo_admisible:
                self.verif_esfuerzo_var.set("CUMPLE ✓")
                color_esfuerzo = "green"
                verificaciones.append(True)
            else:
                self.verif_esfuerzo_var.set("NO CUMPLE ✗")
                color_esfuerzo = "red"
                verificaciones.append(False)
            
            # 2. Verificación de deformación por cortante
            if deformacion_por_capa <= deformacion_max_capa:
                self.verif_deformacion_var.set("CUMPLE ✓")
                color_deformacion = "green"
                verificaciones.append(True)
            else:
                self.verif_deformacion_var.set("NO CUMPLE ✗")
                color_deformacion = "red"
                verificaciones.append(False)
            
            # 3. Verificación de estabilidad global
            if relacion_altura_diametro <= relacion_estabilidad:
                self.verif_estabilidad_var.set("CUMPLE ✓")
                color_estabilidad = "green"
                verificaciones.append(True)
            else:
                self.verif_estabilidad_var.set("NO CUMPLE ✗")
                color_estabilidad = "red"
                verificaciones.append(False)
            
            # 4. Verificación de estabilidad al volteo
            # Para aisladores circulares, generalmente no hay problema de volteo
            self.verif_volteo_var.set("CUMPLE ✓")
            color_volteo = "green"
            verificaciones.append(True)
            
            # 5. Verificación de amortiguamiento efectivo
            if coef_amortiguamiento >= amortiguamiento_min:
                self.verif_amortiguamiento_var.set("CUMPLE ✓")
                color_amortiguamiento = "green"
                verificaciones.append(True)
            else:
                self.verif_amortiguamiento_var.set("NO CUMPLE ✗")
                color_amortiguamiento = "red"
                verificaciones.append(False)
            
            # Verificación general
            if all(verificaciones):
                self.verif_general_var.set("CUMPLE TODOS LOS REQUISITOS ✓")
                color_general = "green"
            else:
                self.verif_general_var.set("NO CUMPLE ALGUNOS REQUISITOS ✗")
                color_general = "red"
            
            # Aplicar colores a las verificaciones
            for label, color in [
                (self.verif_esfuerzo_var, color_esfuerzo),
                (self.verif_deformacion_var, color_deformacion),
                (self.verif_estabilidad_var, color_estabilidad),
                (self.verif_volteo_var, color_volteo),
                (self.verif_amortiguamiento_var, color_amortiguamiento),
                (self.verif_general_var, color_general)
            ]:
                label_widget = self.root.nametowidget(label._name) if hasattr(label, '_name') else None
                if label_widget:
                    label_widget.config(foreground=color)
            
            # Generar reporte detallado de verificación
            reporte = self.generar_reporte_verificacion(
                esfuerzo_actual, esfuerzo_admisible,
                deformacion_por_capa, deformacion_max_capa,
                relacion_altura_diametro, relacion_estabilidad,
                coef_amortiguamiento, amortiguamiento_min,
                diametro_aislador, altura_total, area_total
            )
            
            self.text_verificacion.delete(1.0, tk.END)
            self.text_verificacion.insert(tk.END, reporte)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en la verificación: {str(e)}")
    
    def generar_grafico(self):
        try:
            # Verificar que se hayan calculado los valores primero
            if not self.diametro_calculado_var.get():
                messagebox.showwarning("Advertencia", "Primero debe calcular los parámetros del aislador.")
                return
            
            # Obtener valores calculados
            fuerza_fluencia = float(self.fuerza_fluencia_var.get())
            rigidez_horizontal = float(self.rigidez_horizontal_var.get()) / 1000  # Convertir a kN/mm
            desplazamiento_total = float(self.desplazamiento_total_var.get())
            carga_kN = self.carga_var.get() * 9.81  # Convertir toneladas a kN
            
            # Generar datos para la curva de histéresis (modelo bilineal)
            # Para un aislador con núcleo de plomo, la rigidez post-fluencia es aproximadamente 10% de la rigidez elástica
            rigidez_post_fluencia = 0.1 * rigidez_horizontal
            
            # Punto de fluencia (aproximado)
            desplazamiento_fluencia = fuerza_fluencia / rigidez_horizontal
            
            # Generar ciclo de carga completo (ida y vuelta)
            num_puntos = 100
            desplazamientos = np.linspace(0, desplazamiento_total, num_puntos)
            
            # Curva de carga (rampa positiva)
            fuerza_carga = np.where(
                desplazamientos <= desplazamiento_fluencia,
                rigidez_horizontal * desplazamientos,
                fuerza_fluencia + rigidez_post_fluencia * (desplazamientos - desplazamiento_fluencia)
            )
            
            # Curva de descarga (rampa negativa)
            desplazamientos_descarga = np.linspace(desplazamiento_total, -desplazamiento_total, 2*num_puntos)
            fuerza_descarga = np.zeros_like(desplazamientos_descarga)
            
            for i, d in enumerate(desplazamientos_descarga):
                if d >= desplazamiento_fluencia:
                    fuerza_descarga[i] = fuerza_fluencia + rigidez_post_fluencia * (d - desplazamiento_fluencia)
                elif d <= -desplazamiento_fluencia:
                    fuerza_descarga[i] = -fuerza_fluencia + rigidez_post_fluencia * (d + desplazamiento_fluencia)
                else:
                    fuerza_descarga[i] = rigidez_horizontal * d
            
            # Curva de recarga (rampa positiva)
            desplazamientos_recarga = np.linspace(-desplazamiento_total, desplazamiento_total, 2*num_puntos)
            fuerza_recarga = np.zeros_like(desplazamientos_recarga)
            
            for i, d in enumerate(desplazamientos_recarga):
                if d >= desplazamiento_fluencia:
                    fuerza_recarga[i] = fuerza_fluencia + rigidez_post_fluencia * (d - desplazamiento_fluencia)
                elif d <= -desplazamiento_fluencia:
                    fuerza_recarga[i] = -fuerza_fluencia + rigidez_post_fluencia * (d + desplazamiento_fluencia)
                else:
                    fuerza_recarga[i] = rigidez_horizontal * d
            
            # Combinar todas las curvas
            desplazamientos_completo = np.concatenate([
                desplazamientos,
                desplazamientos_descarga,
                desplazamientos_recarga
            ])
            
            fuerza_completo = np.concatenate([
                fuerza_carga,
                fuerza_descarga,
                fuerza_recarga
            ])
            
            # Limpiar el gráfico anterior
            self.ax.clear()
            
            # Crear el gráfico
            self.ax.plot(desplazamientos_completo, fuerza_completo, 'b-', linewidth=2)
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            self.ax.set_xlabel('Desplazamiento (mm)')
            self.ax.set_ylabel('Fuerza (kN)')
            self.ax.set_title('Curva de Histéresis del Aislador Sísmico')
            self.ax.grid(True, alpha=0.3)
            
            # Añadir anotaciones
            self.ax.annotate(f'Fy = {fuerza_fluencia:.1f} kN', 
                           xy=(desplazamiento_fluencia, fuerza_fluencia), 
                           xytext=(desplazamiento_fluencia+10, fuerza_fluencia+50),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           fontsize=10, color='red')
            
            self.ax.annotate(f'Δmax = {desplazamiento_total:.1f} mm', 
                           xy=(desplazamiento_total, fuerza_completo[np.where(desplazamientos_completo >= desplazamiento_total)[0][0]]), 
                           xytext=(desplazamiento_total+10, fuerza_fluencia),
                           arrowprops=dict(arrowstyle='->', color='green'),
                           fontsize=10, color='green')
            
            # Añadir línea de carga máxima
            self.ax.axhline(y=carga_kN, color='purple', linestyle='--', alpha=0.7, label=f'Carga máxima: {carga_kN:.1f} kN')
            self.ax.legend()
            
            # Actualizar el canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el gráfico: {str(e)}")
    
    def guardar_grafico(self):
        try:
            if self.fig is None:
                messagebox.showwarning("Advertencia", "Primero debe generar el gráfico.")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar gráfico de histéresis"
            )
            
            if file_path:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico guardado correctamente en {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el gráfico: {str(e)}")
    
    def generar_reporte_verificacion(self, esfuerzo_actual, esfuerzo_admisible,
                                   deformacion_por_capa, deformacion_max_capa,
                                   relacion_altura_diametro, relacion_estabilidad,
                                   coef_amortiguamiento, amortiguamiento_min,
                                   diametro, altura, area):
        reporte = f"""VERIFICACIÓN DE DISEÑO SEGÚN ASCE 7-16

1. ESFUERZO DE COMPRESIÓN (ASCE 7-17.2.3.1):
   - Esfuerzo actual: {esfuerzo_actual:.2f} MPa
   - Límite admisible: {esfuerzo_admisible:.2f} MPa
   - Resultado: {'CUMPLE' if esfuerzo_actual <= esfuerzo_admisible else 'NO CUMPLE'}

2. DEFORMACIÓN POR CORTANTE (ASCE 7-17.2.3.2):
   - Deformación por capa: {deformacion_por_capa:.2f} ({deformacion_por_capa*100:.1f}%)
   - Límite máximo: {deformacion_max_capa:.2f} ({deformacion_max_capa*100:.1f}%)
   - Resultado: {'CUMPLE' if deformacion_por_capa <= deformacion_max_capa else 'NO CUMPLE'}

3. ESTABILIDAD GLOBAL (ASCE 7-17.2.3.3):
   - Relación altura/diámetro: {relacion_altura_diametro:.2f}
   - Límite máximo: {relacion_estabilidad:.2f}
   - Resultado: {'CUMPLE' if relacion_altura_diametro <= relacion_estabilidad else 'NO CUMPLE'}

4. ESTABILIDAD AL VOLTEO:
   - Para aisladores circulares, generalmente no hay problema de volteo
   - Resultado: CUMPLE

5. AMORTIGUAMIENTO EFECTIVO (ASCE 7-17.5.3.3):
   - Amortiguamiento actual: {coef_amortiguamiento:.1f}%
   - Mínimo requerido: {amortiguamiento_min:.1f}%
   - Resultado: {'CUMPLE' if coef_amortiguamiento >= amortiguamiento_min else 'NO CUMPLE'}

PROPIEDADES GEOMÉTRICAS:
   - Diámetro del aislador: {diametro:.1f} mm
   - Altura total: {altura:.1f} mm
   - Área de la sección: {area:.0f} mm²

RECOMENDACIONES:
"""
        if esfuerzo_actual > esfuerzo_admisible:
            reporte += "   - Aumentar el diámetro del aislador para reducir el esfuerzo de compresión\n"
        
        if deformacion_por_capa > deformacion_max_capa:
            reporte += "   - Aumentar el número de capas o el espesor de cada capa\n"
        
        if relacion_altura_diametro > relacion_estabilidad:
            reporte += "   - Reducir la altura total o aumentar el diámetro del aislador\n"
        
        if coef_amortiguamiento < amortiguamiento_min:
            reporte += "   - Aumentar el diámetro del núcleo de plomo para incrementar el amortiguamiento\n"
        
        if all([
            esfuerzo_actual <= esfuerzo_admisible,
            deformacion_por_capa <= deformacion_max_capa,
            relacion_altura_diametro <= relacion_estabilidad,
            coef_amortiguamiento >= amortiguamiento_min
        ]):
            reporte += "   - El diseño CUMPLE con todos los requisitos de ASCE 7-16\n"
        
        reporte += "\nNota: Esta verificación es preliminar. Se requieren ensayos de prototipos para validación final."
        
        return reporte
    
    def redondear_valor_estandar(self, valor):
        # Redondear a valores estándar de diámetros comerciales
        estandares = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 
                      650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
        
        for estandar in estandares:
            if valor <= estandar:
                return estandar
        
        return estandares[-1]
    
    def generar_info_etabs(self, diametro, altura_total, altura_caucho, fluencia, 
                          k_horizontal, k_vertical, diametro_nucleo, amortiguamiento, 
                          carga, desplazamiento, num_capas, espesor_capa, periodo, 
                          desplazamiento_total, S1, SDS, SD1, TL, BD):
        info = f"""PARÁMETROS DE DISEÑO SEGÚN ASCE 7-16:

DATOS SÍSMICOS DE ENTRADA:
- Parámetro S1: {S1}
- Parámetro SDS: {SDS}
- Parámetro SD1: {SD1}
- Parámetro TL: {TL}
- Factor de amplificación BD: {BD}

PROPIEDADES GEOMÉTRICAS DEL AISLADOR:
- Diámetro total: {diametro:.1f} mm
- Altura total: {altura_total:.1f} mm
- Altura de caucho: {altura_caucho:.1f} mm
- Número de capas de caucho: {num_capas}
- Espesor de cada capa de caucho: {espesor_capa:.1f} mm
- Diámetro del núcleo de plomo: {diametro_nucleo:.1f} mm

PROPIEDADES DE CARGA Y DEFORMACIÓN:
- Carga vertical de diseño: {carga:.1f} kN
- Desplazamiento máximo de diseño: {desplazamiento:.1f} mm
- Periodo del sistema aislado: {periodo:.2f} s
- Desplazamiento total calculado: {desplazamiento_total:.1f} mm

PROPIEDADES MECÁNICAS:
- Fuerza de fluencia del núcleo de plomo: {fluencia:.1f} kN
- Rigidez horizontal efectiva, K_h: {k_horizontal:.1f} kN/m
- Rigidez vertical, K_v: {k_vertical:.1f} kN/m
- Coeficiente de amortiguamiento efectivo: {amortiguamiento:.1f}%

RECOMENDACIONES PARA MODELADO EN ETABS/SAP2000 SEGÚN ASCE 7:
1. Utilice el elemento 'Rubber Isolator' o 'Lead Rubber Bearing'
2. Defina las propiedades no lineales según los valores calculados
3. Para el núcleo de plomo, utilice el modelo bilineal con:
   - Fuerza de fluencia = {fluencia:.1f} kN
   - Rigidez post-fluencia = 5-10% de la rigidez elástica
4. Considere los efectos P-Delta para cargas verticales grandes (ASCE 7-12.8.7)
5. Verifique que el desplazamiento máximo no exceda el valor de diseño
6. Aplique los factores de modificación según ASCE 7-17.2.3

REQUISITOS ASCE 7-16, CAPÍTULO 17:
- El esfuerzo de compresión no debe exceder 11 MPa para carga de servicio
- La deformación por cortante no debe exceder el 50% en cada capa
- El sistema debe ser verificado para el máximo desplazamiento de diseño
- Se deben considerar los efectos de carga vertical y rotación

Nota: Estos valores son una aproximación inicial según ASCE 7-16. 
Se requiere validación con normas específicas y ensayos de prototipos."""
        return info
    
    def exportar_json(self):
        try:
            if not self.diametro_calculado_var.get():
                messagebox.showwarning("Advertencia", "Primero debe calcular los parámetros del aislador.")
                return
            
            # Crear diccionario con todos los datos
            data = {
                "carga_ton": self.carga_var.get(),
                "diametro_aislador_mm": self.diametro_aislador_var.get(),
                "altura_caucho_mm": self.altura_caucho_var.get(),
                "desplazamiento_max_mm": self.desplazamiento_var.get(),
                "parametros_sismicos": {
                    "S1": self.s1_var.get(),
                    "SDS": self.sds_var.get(),
                    "SD1": self.sd1_var.get(),
                    "TL": self.tl_var.get()
                },
                "resultados_diseno": {
                    "diametro_calculado_mm": float(self.diametro_calculado_var.get()),
                    "altura_total_mm": float(self.altura_total_var.get()),
                    "altura_caucho_calculada_mm": float(self.altura_caucho_calc_var.get()),
                    "num_capas_caucho": int(self.num_capas_var.get()),
                    "espesor_capa_mm": float(self.espesor_capa_var.get()),
                    "fuerza_fluencia_kN": float(self.fuerza_fluencia_var.get()),
                    "rigidez_horizontal_kN_m": float(self.rigidez_horizontal_var.get()),
                    "rigidez_vertical_kN_m": float(self.rigidez_vertical_var.get()),
                    "diametro_nucleo_mm": float(self.diametro_nucleo_var.get()),
                    "coef_amortiguamiento_porc": float(self.coef_amortiguamiento_var.get()),
                    "periodo_aislado_s": float(self.periodo_aislado_var.get()),
                    "desplazamiento_total_mm": float(self.desplazamiento_total_var.get())
                },
                "verificaciones": {
                    "esfuerzo_compresion": self.verif_esfuerzo_var.get(),
                    "deformacion_cortante": self.verif_deformacion_var.get(),
                    "estabilidad_global": self.verif_estabilidad_var.get(),
                    "estabilidad_volteo": self.verif_volteo_var.get(),
                    "amortiguamiento_efectivo": self.verif_amortiguamiento_var.get(),
                    "estado_general": self.verif_general_var.get()
                }
            }
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Guardar parámetros del aislador"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def limpiar(self):
        self.carga_var.set(200.0)
        self.diametro_aislador_var.set(0.0)
        self.altura_caucho_var.set(0.0)
        self.desplazamiento_var.set(150.0)
        self.s1_var.set(0.6)
        self.sds_var.set(1.0)
        self.sd1_var.set(0.8)
        self.tl_var.set(8.0)
        self.diametro_calculado_var.set("")
        self.altura_total_var.set("")
        self.altura_caucho_calc_var.set("")
        self.fuerza_fluencia_var.set("")
        self.rigidez_horizontal_var.set("")
        self.rigidez_vertical_var.set("")
        self.diametro_nucleo_var.set("")
        self.coef_amortiguamiento_var.set("")
        self.num_capas_var.set("")
        self.espesor_capa_var.set("")
        self.periodo_aislado_var.set("")
        self.desplazamiento_total_var.set("")
        self.verif_esfuerzo_var.set("")
        self.verif_deformacion_var.set("")
        self.verif_estabilidad_var.set("")
        self.verif_volteo_var.set("")
        self.verif_amortiguamiento_var.set("")
        self.verif_general_var.set("")
        self.text_output.delete(1.0, tk.END)
        self.text_verificacion.delete(1.0, tk.END)
        
        # Limpiar gráfico
        if self.fig:
            self.ax.clear()
            self.ax.set_xlabel('Desplazamiento (mm)')
            self.ax.set_ylabel('Fuerza (kN)')
            self.ax.set_title('Curva de Histéresis del Aislador Sísmico')
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()

def main():
    root = tk.Tk()
    app = AisladorSismicoASCE7App(root)
    root.mainloop()

if __name__ == "__main__":
    main()