# ---------------------------------------------------------
# KRESLENIE
# ---------------------------------------------------------
def draw(self):
    self.screen.fill((20, 20, 20))

    # 1) Notová osnova
    self.staff_ui.draw(self.screen)

    # 2) Grafický renderer
    renderer_surface = self.renderer.render()
    self.screen.blit(renderer_surface, (0, 200))

    # 3) Piano roll – posunutý nižšie, aby sa neprekrýval
    self.piano_ui.draw()
    self.screen.blit(self.piano_ui.screen, (0, 400))

    # 4) Note visualizer – voliteľné (mimo obrazovky pri výške 600)
    visual_surface = pygame.Surface((self.width, 200))
    self.note_visualizer.draw(visual_surface)
    # self.screen.blit(visual_surface, (0, 600))  # ak chceš

    # BPM text
    bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
    self.screen.blit(bpm_surface, (10, 10))

    # Aktívny track
    active_track = self.track_system.get_active_track()
    if active_track is not None:
        track_text = f"Track {active_track.id}: {active_track.name} (CH {active_track.channel})"
        color = active_track.color if hasattr(active_track, "color") else (200, 200, 200)
        track_surface = self.small_font.render(track_text, True, color)
        self.screen.blit(track_surface, (300, 10))

    # BPM vizualizácia
    if self.bpm_value is not None:
        self.draw_bpm_visual()

    self.draw_bpm_history()

    pygame.display.flip()


# ---------------------------------------------------------
# HLAVNÁ SLUČKA UI
# ---------------------------------------------------------
def run(self):
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 🔥 Renderer spracuje eventy až po event loope
        self.renderer.run_event_loop_step()

        self.draw()
        clock.tick(60)

    pygame.quit()
