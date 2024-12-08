from turtle import width
import flet as ft
from flet_core.box import Gradient
import pygame
import os
from mutagen.mp3 import MP3
import asyncio


#Definim la classe Song i assignem els seus atributs
class Song:
    def __init__(self, filename):
        self.filename = filename
        parts = filename.split(".")
        self.title = parts[0]
        self.duration = self.get_duration()
        self.artist = parts[1]
        self.genre = parts[2]
        self.index = 0
        
    #Funcio que ens retorna la durada de la canco    
    def get_duration(self):
        audio = MP3(os.path.join("music", self.filename))
        return audio.info.length

class Playlist:
    def __init__(self,name):
        self.name = name
        self.canciones = []
        

async def main(page: ft.Page):
    #Titol de pagina, color del fons, inicialitzacio del mixer...
    page.title = "Reproductor de Musica"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.colors.BLUE_GREY_800
    page.padding = 20
    titulo = ft.Text(value="Mi Reproductor MP3", size=30)
    pygame.mixer.init()
    #Creem una llista amb totes les cancons
    all_music = [Song(f) for f in os.listdir("music") if f.endswith(".mp3")]

    #La variable playlist es la playlist que esta carregada actualment
    playlist = []
    playlists = []
    current_playlist_index = 0
    current_song_index = 0  #Index de canco actual
    #Funcio per carregar una canco
    def load_song():
        pygame.mixer.music.load(os.path.join("music", playlist.canciones[current_song_index].filename))
        update_song_info()
    #Funcio per anar enrere una canco
    def prev_song(e):
        nonlocal current_song_index
        current_song_index = (current_song_index -1)% len(playlist.canciones)
        load_song()
        pygame.mixer.music.play()
        play_button.icon= ft.icons.PAUSE
        page.update()
    #Funcio per anar endavant una canco
    def next_song(e):
        nonlocal current_song_index
        current_song_index = (current_song_index +1)% len(playlist.canciones)
        load_song()
        pygame.mixer.music.play()
        play_button.icon= ft.icons.PAUSE
        page.update()
    #Funcio de play,pausa en funcio de quina es la situacio i canviem el icon 
    def play_pause(e):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            play_button.icon = ft.icons.PLAY_ARROW
        else:
            if pygame.mixer.music.get_pos() == -1:
                load_song()
                pygame.mixer.music.play() 
            else:
                pygame.mixer.music.unpause()
            play_button.icon = ft.icons.PAUSE
        page.update()
    #Funcio per quan cliquejem a una canco
    def click_on_song(e,indice):
        nonlocal current_song_index 
        current_song_index = indice
        load_song()
        pygame.mixer.music.play() 
        play_button.icon = ft.icons.PAUSE
        page.update()

    def get_index_song_actual(name):
        nonlocal playlists
        for i, cancion in enumerate(playlist.canciones):
            if cancion.title == name:
                return i

    #Funcio per passar a la seguent canco automaticament quan sacaba la que es reprodueix
    def next_song_auto():
        nonlocal current_song_index
        current_song_index = (current_song_index +1)% len(playlist.canciones)
        load_song()
        pygame.mixer.music.play()
        play_button.icon= ft.icons.PAUSE
        page.update()


    def update_song_info():
        nonlocal current_position
        current_position= 0.0
        song = playlist.canciones[current_song_index]
        song_info.value= f"{song.title} \n {song.artist}"
        duration.value = format_time(song.duration)
        progress_slider.value = 0.0
        current_time_text = "00:00"
        page.update()

    def format_time(segundos):
        minutos= segundos // 60
        segundos_restantes = segundos % 60
        return f"{int(minutos):02}:{int(segundos_restantes):02}"

    def get_index_playlist_actual(name):
        nonlocal playlists
        for i, playlist in enumerate(playlists):
            if playlist.name == name:
                return i
    #Definim les funcions per el slider, hi ha un fil que ha d'anar actualitzantlo automaticament pero quan el modifiquem manualment ha de parar
    #d'actualitzar, si no hi han problemes de concurrencia aixi que crearem funcions per dir qui pot 
    is_slider_active = False
    current_position = 0.0
    def start_slider_interaction(e):
        nonlocal is_slider_active
        is_slider_active = True
        
            
        

    def end_slider_interaction(e):
       
            nonlocal is_slider_active
            nonlocal current_position
            current_position = progress_slider.value * playlist.canciones[current_song_index].duration
            pygame.mixer.music.play(start=current_position)
            print(f" Despues de set {current_position}")
            progress_slider.value = current_position / playlist.canciones[current_song_index].duration
            current_time_text.value = format_time(current_position)  
            page.update()
            is_slider_active = False
            
        


    async def update_progress():
        
            while True:
                nonlocal playlist
                nonlocal current_song_index
                nonlocal current_position
                nonlocal is_slider_active
           
                if is_slider_active == False and pygame.mixer.music.get_busy():
                    new_position =current_position + (pygame.mixer.music.get_pos() / 1000)
                    progress_slider.value = new_position / playlist.canciones[current_song_index].duration
                    current_time_text.value = format_time(new_position)
                    page.update()
                    print(f"{new_position}")
                    if (playlist.canciones[current_song_index].duration - new_position) < 1 :
                        next_song_auto()

                
                
                await asyncio.sleep(1)
            
            
            
        
        
        
            

    def update_song_position(e):
        global current_position
        
        if playlist.canciones and pygame.mixer.music.get_busy():
            current_position = progress_slider.value * playlist.canciones[current_song_index].duration
            pygame.mixer.music.set_pos(current_position)  
            print(f" Despues de set {pygame.mixer.music.get_pos() / 1000}")
            progress_slider.value = current_position / playlist.canciones[current_song_index].duration
            current_time_text.value = format_time(current_position)  
            page.update()

    seleccionadas= []
    def seleccionar_cancion(e):
        
        nonlocal canciones_para_seleccionar
        nonlocal seleccionadas
        seleccionadas = [s for s in canciones_para_seleccionar if s.leading.value]
        
        
    def crear_playlist_nueva(e,name):
        nonlocal playlists
        nonlocal grid
        nonlocal canciones_seleccionadas
        nonlocal seleccionadas
        contenedor = ft.Container(
        content=ft.Text(value = name, size = 18, weight= ft.FontWeight.BOLD, color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_300,
        width=200,
        height=200,
        border_radius = 10,
        alignment=ft.alignment.center,
        ink=True,
        on_click= lambda e: mostrar_pagina_playlist(e,name)
        )
        grid.controls.append(contenedor)
        p = Playlist(name)
        for s in seleccionadas:
            for cancion in all_music:
                if s.title.value == cancion.title:
                    canciones_seleccionadas.append(cancion)
        i=0
        for s in canciones_seleccionadas:    
                s.index = i
                p.canciones.append(s)
                i = i+1
        playlists.append(p)
        canciones_seleccionadas=[]
        barra_de_texto.value=""

        mostrar_pagina_principal()

            

    def mostrar_pagina_playlist(e,name):
        titulo_principal.value = (name)
        nonlocal playlist
        columna_canciones.controls.clear()
        nonlocal current_song_index
        current_song_index= 0
        
        playlist = playlists[get_index_playlist_actual(name)]
        
        
        for s in playlist.canciones:
            
            cancion = ft.Container(
                content= ft.Text(value=f"{s.title}  |  {s.artist}", size=12,color=ft.colors.WHITE),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.RED_300,
                ink=True,
                ink_color=ft.colors.RED_700,
                border_radius=10,
                width=page.width,
                height=30,
                on_click=lambda e, idx= get_index_song_actual(s.title) : click_on_song(e,idx),    
                )
            
            columna_canciones.controls.append(cancion)
            
        
        page.controls.clear()  # Limpiar los controles actuales
        page.add(layout_secundario)  # Anadir el layout secundario
        page.update()

    def mostrar_pagina_principal():
        titulo_principal.value = ("REPRODUCTOR AJ")
        page.controls.clear()
        page.add(layout_principal)
        page.update()

    def mostrar_layout_creando_playlist():
        page.controls.clear()
        page.add(layout_creando_playlist)
        page.update()


    def create_playlist_genre(name,genre):
        nonlocal playlists
        stringn = f"{name}"
        stringg = f"{genre}"
        contenedor = ft.Container(
        content=ft.Text(value = name, size = 18, weight= ft.FontWeight.BOLD, color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_300,
        width=200,
        height=200,
        border_radius = 10,
        alignment=ft.alignment.center,
        ink=True,
        on_click= lambda e: mostrar_pagina_playlist(e,name)
        )
        grid.controls.append(contenedor)
        p = Playlist(name)
        i=0
        for s in all_music:
            if s.genre == genre:
                s.index = i
                p.canciones.append(s)
                i = i+1
        playlists.append(p)








    # Definim els elements del reproductor
    song_info = ft.Text(size=20, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
    current_time_text = ft.Text(value="00:00")
    duration = ft.Text(value="00:00")
    progress_slider = ft.Slider(value=0.0, min=0.0,max=1.0,expand=True, inactive_color=ft.colors.RED,active_color=ft.colors.WHITE,
                                on_change=lambda e: start_slider_interaction(e),
                                on_change_end=lambda e: end_slider_interaction(e),

                                )
    play_button = ft.IconButton(icon=ft.icons.PLAY_ARROW, icon_color=ft.colors.WHITE, on_click=play_pause)
    prev_button = ft.IconButton(icon=ft.icons.SKIP_PREVIOUS, icon_color=ft.colors.WHITE, on_click = prev_song)
    next_button = ft.IconButton(icon=ft.icons.SKIP_NEXT, icon_color=ft.colors.WHITE, on_click = next_song)

    # Elementos de la playlist


    controls = ft.Row(
        [prev_button, play_button, next_button],
        alignment=ft.MainAxisAlignment.CENTER
    )

    fila_reproductor = ft.Row(
        [current_time_text, progress_slider, duration],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    reproductor = ft.Column(
        [song_info, fila_reproductor, controls],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment= ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    contenedor_reproductor = ft.Container(
        content= reproductor,
        bgcolor= ft.colors.BLACK26,
        border_radius= 20,
        alignment = ft.alignment.bottom_center,
        padding=10,

        )


     #Elementos de la pagina de inicio:
    titulo_principal = ft.Text(value="AJ MUSIC", size=20,color=ft.colors.WHITE, weight=ft.FontWeight.BOLD,text_align=ft.alignment.center, expand=True,)
    grid = ft.GridView(
        expand = True,
        max_extent=220,
        spacing=10,
        run_spacing=10,
        auto_scroll=True,
        )
    #Creamos los contenedores de genero y un contenedor para agregar una nuvea playlist
    create_playlist_genre("RAP","Rap")
    create_playlist_genre("REGGAETON","Reggaeton")
    create_playlist_genre("TECHNO","Techno")
    create_playlist_genre("JAZZ","Jazz")
    create_playlist_genre("POP","Pop")
    create_playlist_genre("ROCK","Rock")
    

    #Layout Principal:
    
    layout_principal = ft.Column(
        [
            ft.Container(
            content=ft.Row([titulo_principal,ft.IconButton(icon=ft.icons.ADD,icon_color=ft.colors.WHITE, on_click= lambda e: mostrar_layout_creando_playlist())]),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.BLACK26   ,
            padding=10,
            border_radius=10,
            height=60,
        ),
        
        
        ft.Container(
            content=grid,
            border_radius = 10,
            expand=True,
            
            
        ),
            contenedor_reproductor,
        ],
        expand=True,
    )
    #Elementos del Layout Secundario:
    columna_canciones = ft.Column([],
                                  scroll=ft.ScrollMode.AUTO,
                                  expand=True,
                                  
                                  
                                  )


    #Layout Secundario:
    atras_titulo = ft.Row(controls = [ft.IconButton( icon= ft.icons.ARROW_BACK,icon_color=ft.colors.WHITE,on_click= lambda e: mostrar_pagina_principal()),
                                      titulo_principal],
                         )
    
    layout_secundario = ft.Column(
    [
        # Titulo fijo arriba
        ft.Container(
            content=atras_titulo,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.BLACK26   ,
            padding=10,
            border_radius=10,
            height=60,
        ),
        
        # Lista de canciones con scroll
        ft.Container(
            content=columna_canciones,
            border_radius = 10,
            expand=True,
            
            
        ),
        # Reproductor fijo abajo
        
            contenedor_reproductor,
           


        
    ],
    expand=True,
    spacing=20,  # Sin espacios extra entre los contenedores
    )

    #Elementos y Layout_creando_playlist
    barra_de_texto = ft.TextField(hint_text="Nombre de tu Playlist",
                                  bgcolor=ft.colors.RED_300,
                                  border_color=ft.colors.WHITE,
                                  color=ft.colors.WHITE,
                                  border_radius=10,
                                  expand=True,
                                  
                                  )
    boton_submit = ft.ElevatedButton(text="Submit",
                                     on_click=lambda e: crear_playlist_nueva(e,barra_de_texto.value)
                                     )
    canciones_para_seleccionar = []
    canciones_seleccionadas = []
    lista_all_music = ft.ListView(auto_scroll=True,
                                  spacing=10,
                                  expand=True,
                                  )
    for s in all_music:
        s = ft.ListTile(title=ft.Text(value=f"{s.title}", size=12,color=ft.colors.WHITE),
                        subtitle=ft.Text(value=f"{s.artist}", size=12,color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_300,
                        leading= ft.Checkbox(on_change=lambda e: seleccionar_cancion(e))
                        
                        )
        lista_all_music.controls.append(s)
        canciones_para_seleccionar.append(s)
    columna_layout_crear_playlist = ft.Column([ft.Row([barra_de_texto,boton_submit], height=50,width=page.width,),lista_all_music],
                                              expand=True,
                                              width=page.width,
                                              height=page.height,
                                              )
    contenedor_layout_crear_playlist = ft.Container(
        content=columna_layout_crear_playlist,
        bgcolor=ft.colors.RED_300,
        width=page.width,
        expand=True,
        border_radius = 10,
        alignment=ft.alignment.center,
        ink=True,
        padding=0,
       
        )
    layout_creando_playlist = contenedor_layout_crear_playlist

                                                    
                                                    
                                                    

    
 

    




    # Anadir elementos a la pagina
    
   
    mostrar_pagina_principal()
    await update_progress()
    

    
ft.app(target=main)
