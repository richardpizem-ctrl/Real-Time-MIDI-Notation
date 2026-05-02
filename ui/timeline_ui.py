    # ---------------------------------------------------------
    # EVENTS (v2.0.0 – stabilná verzia)
    # ---------------------------------------------------------
    def handle_event(self, event) -> Optional[None]:
        mx, my = pygame.mouse.get_pos()
        self.mouse_x, self.mouse_y = mx, my

        # -----------------------------------------------------
        # HOVER DETECTION FOR MARKERS
        # -----------------------------------------------------
        self.hover_marker_index = None
        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)
            if rect.collidepoint((mx, my)):
                self.hover_marker_index = i
                break

        # -----------------------------------------------------
        # MOUSE DOWN
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            # LEFT CLICK
            if event.button == 1:
                # 1) Marker rename commit
                if self.marker_rename_index is not None:
                    self._commit_marker_rename()

                # 2) Click on marker → drag or rename
                if self.hover_marker_index is not None:
                    # Double-click → rename
                    now = pygame.time.get_ticks()
                    if (
                        self._last_click_marker_index == self.hover_marker_index
                        and now - self._last_click_time <= self._double_click_threshold_ms
                    ):
                        self._start_marker_rename(self.hover_marker_index)
                    else:
                        self._start_marker_drag(self.hover_marker_index, mx)

                    self._last_click_marker_index = self.hover_marker_index
                    self._last_click_time = now
                    return

                # 3) Click on loop handles
                loop_rect = self._compute_loop_rect()
                if loop_rect:
                    handle_w = 4
                    left_handle = pygame.Rect(loop_rect.x - handle_w, loop_rect.y, handle_w, loop_rect.h)
                    right_handle = pygame.Rect(loop_rect.right, loop_rect.y, handle_w, loop_rect.h)

                    if left_handle.collidepoint((mx, my)):
                        self.loop_resizing_left = True
                        return
                    if right_handle.collidepoint((mx, my)):
                        self.loop_resizing_right = True
                        return
                    if loop_rect.collidepoint((mx, my)):
                        self.loop_dragging = True
                        self.loop_drag_offset = (
                            self.controller.layout.pixel_to_beat(mx - self.x + self.scroll_x)
                            - self.loop_start_beat
                        )
                        return

                # 4) Click on scroll handle
                handle = self._compute_handle_rect()
                if handle.collidepoint((mx, my)):
                    self._start_handle_drag(mx)
                    return

                # 5) Click on scroll bar
                if self.scroll_bar_rect.collidepoint((mx, my)):
                    self._start_handle_drag(mx)
                    return

                # 6) Click on zoom bar
                if self.zoom_bar_rect.collidepoint((mx, my)):
                    rel = (mx - self.zoom_bar_rect.x) / max(1, self.zoom_bar_rect.w)
                    self.zoom = max(0.3, min(4.0, rel * 4.0))
                    return

                # 7) Click on ruler → set playhead
                ruler_bottom = self.y + self.ruler_height
                if self.y <= my <= ruler_bottom:
                    beat = self.controller.layout.pixel_to_beat(mx - self.x + self.scroll_x)
                    beat = max(0.0, beat)
                    if hasattr(self.controller, "set_playhead_beat"):
                        try:
                            self.controller.set_playhead_beat(beat)
                        except Exception:
                            pass
                    return

                # 8) Click on empty grid → start loop
                grid_top = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
                grid_bottom = self.y + self.height - (self.zoom_bar_rect.h + self.scroll_bar_rect.h)
                if grid_top <= my <= grid_bottom:
                    self._start_loop(mx)
                    return

            # RIGHT CLICK → drag scroll
            if event.button == 3:
                self.dragging = True
                self.drag_start_x = mx
                self.drag_initial_scroll = self.scroll_x
                return

        # -----------------------------------------------------
        # MOUSE UP
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # finalize marker drag
                if self.marker_dragging is not None:
                    self._end_marker_drag()

                # finalize loop
                if self.loop_resizing_left or self.loop_resizing_right or self.loop_dragging:
                    self.loop_resizing_left = False
                    self.loop_resizing_right = False
                    self.loop_dragging = False
                    self._finalize_loop()

                # finalize handle drag
                if self.handle_dragging:
                    self._end_handle_drag()

            if event.button == 3:
                self.dragging = False

        # -----------------------------------------------------
        # MOUSE MOTION
        # -----------------------------------------------------
        if event.type == pygame.MOUSEMOTION:
            # marker drag
            if self.marker_dragging is not None:
                self._update_marker_drag(mx)
                return

            # loop resize
            if self.loop_resizing_left:
                beat = self.controller.layout.pixel_to_beat(mx - self.x + self.scroll_x)
                beat = self._snap_beat(beat)
                self.loop_start_beat = max(0.0, beat)
                return

            if self.loop_resizing_right:
                beat = self.controller.layout.pixel_to_beat(mx - self.x + self.scroll_x)
                beat = self._snap_beat(beat)
                self.loop_end_beat = max(0.0, beat)
                return

            # loop drag
            if self.loop_dragging:
                beat = self.controller.layout.pixel_to_beat(mx - self.x + self.scroll_x)
                new_start = beat - self.loop_drag_offset
                new_end = new_start + (self.loop_end_beat - self.loop_start_beat)
                if new_start >= 0:
                    self.loop_start_beat = new_start
                    self.loop_end_beat = new_end
                return

            # scroll handle drag
            if self.handle_dragging:
                self._update_handle_drag(mx)
                return

            # drag scroll (right mouse)
            if self.dragging:
                dx = mx - self.drag_start_x
                self.scroll_x = max(0, self.drag_initial_scroll - dx)
                return

        # -----------------------------------------------------
        # MOUSE WHEEL (zoom)
        # -----------------------------------------------------
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.zoom = min(4.0, self.zoom * 1.1)
            else:
                self.zoom = max(0.3, self.zoom * 0.9)
            return
