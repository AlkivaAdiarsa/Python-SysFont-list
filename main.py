import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions and colors
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
BG_COLOR = (255, 255, 255) # White background
TEXT_COLOR_FONT = (0, 0, 0)     # Black text for the specific font render
TEXT_COLOR_ARIAL = (100, 100, 100) # Gray text for the Arial label
FONT_SIZE = 24
LINE_HEIGHT = FONT_SIZE + 15 # Space between lines

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scrollable SysFont List (Rendered + Arial Label)")

# Get list of system fonts (names are lowercase, no spaces)
all_fonts = pygame.font.get_fonts()
all_fonts.sort()

# Define standard Arial/Fallback font objects
try:
    # Try to load Arial
    arial_font_object = pygame.font.SysFont('arial', FONT_SIZE, bold=True)
except Exception:
    # Fallback to default system sans font if Arial is missing
    arial_font_object = pygame.font.SysFont(None, FONT_SIZE, bold=True)

# Use a default fallback font for fonts that fail to render
fallback_font_object = pygame.font.SysFont(None, FONT_SIZE)

# Cache rendered font surfaces: (specific_font_surface, arial_label_surface)
font_surfaces_data = []

for font_name_internal in all_fonts:
    # Prepare the string to display
    text_to_render = f"Example Text in {font_name_internal}"
    
    # 1. Render the label in Arial/Generic font
    arial_label_surface = arial_font_object.render(f"[{font_name_internal}] ->", True, TEXT_COLOR_ARIAL)
    
    # 2. Attempt to render the example text using the specific font
    specific_font_surface = None
    try:
        current_font_object = pygame.font.SysFont(font_name_internal, FONT_SIZE)
        # Use the specific font to render the example text
        specific_font_surface = current_font_object.render(text_to_render, True, TEXT_COLOR_FONT)
        
    except Exception as e:
        # Fallback if the font cannot be loaded or render its name (e.g., missing glyphs)
        print(f"Error with font {font_name_internal}: {e}. Using fallback.")
        text_to_render_fallback = f"FONT ERROR: Cannot render this font."
        specific_font_surface = fallback_font_object.render(text_to_render_fallback, True, (255, 0, 0)) # Red text for error

    # Store both surfaces
    font_surfaces_data.append((arial_label_surface, specific_font_surface))

# Render the text
text_to_display = "SysFont List"
text_color = (0, 0, 0) # White
text_surface =  arial_font_object.render(text_to_display, True, text_color)

# Get the rectangle of the text surface for positioning
text_rect = text_surface.get_rect()
text_rect.center = (SCREEN_WIDTH // 2, 25) # Center the text


# Scrolling variables
scroll_y = 0
content_height = len(font_surfaces_data) * LINE_HEIGHT
content_height += 100
# Content is drawn starting at y=65, so viewport for the list excludes header area
CONTENT_TOP = 65
CONTENT_BOTTOM_PADDING = 10
viewport_height = SCREEN_HEIGHT - CONTENT_TOP - CONTENT_BOTTOM_PADDING

# Scrollbar configuration
SCROLLBAR_WIDTH = 12
SCROLLBAR_PADDING = 8
SCROLLBAR_COLOR = (220, 220, 220)
SCROLLBAR_THUMB_COLOR = (140, 140, 140)
SCROLLBAR_THUMB_MIN_HEIGHT = 30

# Thumb dragging state
dragging_thumb = False
drag_offset_y = 0

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            scroll_y += event.y * 15 # Scroll speed multiplier

            # Constrain scrolling within bounds
            max_scroll = max(0, content_height - viewport_height)
            if scroll_y > 0:
                scroll_y = 0
            if scroll_y < -max_scroll:
                scroll_y = -max_scroll
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                # Build track rect for hit testing
                track_x = SCREEN_WIDTH - SCROLLBAR_WIDTH - SCROLLBAR_PADDING
                track_y = CONTENT_TOP
                track_h = viewport_height
                track_rect = pygame.Rect(track_x, track_y, SCROLLBAR_WIDTH, track_h)

                # Compute thumb size and position
                if content_height > 0 and content_height > viewport_height:
                    thumb_h = max(SCROLLBAR_THUMB_MIN_HEIGHT, int(viewport_height * (viewport_height / content_height)))
                    max_scroll = content_height - viewport_height
                    scroll_pct = (-scroll_y) / max_scroll if max_scroll > 0 else 0
                    thumb_y = int(track_y + scroll_pct * (track_h - thumb_h))
                    thumb_rect = pygame.Rect(track_x, thumb_y, SCROLLBAR_WIDTH, thumb_h)
                else:
                    thumb_rect = pygame.Rect(track_x, track_y, SCROLLBAR_WIDTH, track_h)

                if thumb_rect.collidepoint((mx, my)):
                    dragging_thumb = True
                    drag_offset_y = my - thumb_rect.y
                elif track_rect.collidepoint((mx, my)):
                    # Click on track: move thumb center to mouse and update scroll
                    # Compute new thumb_y then map to scroll_y
                    if content_height > viewport_height:
                        new_thumb_y = max(track_y, min(my - (thumb_rect.height // 2), track_y + track_h - thumb_rect.height))
                        rel = (new_thumb_y - track_y) / (track_h - thumb_rect.height)
                        max_scroll = content_height - viewport_height
                        scroll_y = -int(rel * max_scroll)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_thumb = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_thumb:
                mx, my = event.pos
                track_x = SCREEN_WIDTH - SCROLLBAR_WIDTH - SCROLLBAR_PADDING
                track_y = CONTENT_TOP
                track_h = viewport_height
                if content_height > viewport_height:
                    thumb_h = max(SCROLLBAR_THUMB_MIN_HEIGHT, int(viewport_height * (viewport_height / content_height)))
                    new_thumb_y = max(track_y, min(my - drag_offset_y, track_y + track_h - thumb_h))
                    rel = (new_thumb_y - track_y) / (track_h - thumb_h)
                    max_scroll = content_height - viewport_height
                    scroll_y = -int(rel * max_scroll)

    screen.fill(BG_COLOR)

    # Blit (draw) only the visible font surfaces
    for i, (arial_surf, specific_surf) in enumerate(font_surfaces_data):
        y_pos = i * LINE_HEIGHT + scroll_y + 65
        
        # Only draw if the text is within the screen boundaries
        if y_pos < SCREEN_HEIGHT and y_pos + specific_surf.get_height() > 0:
            # Blit the Arial label first (e.g., at x=10)
            screen.blit(arial_surf, (10, y_pos))
            
            # Blit the specific font surface next to it (e.g., offset by the label width + some padding)
            offset_x = arial_surf.get_width() + 20
            screen.blit(specific_surf, (offset_x, y_pos))

    # Draw header background and title
    pygame.draw.rect(screen, "white", (0, 0, SCREEN_WIDTH, 50),)
    screen.blit(text_surface, text_rect)

    # Draw scrollbar on the right side
    track_x = SCREEN_WIDTH - SCROLLBAR_WIDTH - SCROLLBAR_PADDING
    track_y = CONTENT_TOP
    track_h = viewport_height
    track_rect = pygame.Rect(track_x, track_y, SCROLLBAR_WIDTH, track_h)

    if content_height > viewport_height:
        # Thumb size proportional to viewport/content
        thumb_h = max(SCROLLBAR_THUMB_MIN_HEIGHT, int(viewport_height * (viewport_height / content_height)))
        max_scroll = content_height - viewport_height
        scroll_pct = (-scroll_y) / max_scroll if max_scroll > 0 else 0
        thumb_y = int(track_y + scroll_pct * (track_h - thumb_h))
        thumb_rect = pygame.Rect(track_x, thumb_y, SCROLLBAR_WIDTH, thumb_h)

        pygame.draw.rect(screen, SCROLLBAR_COLOR, track_rect, border_radius=6)
        pygame.draw.rect(screen, SCROLLBAR_THUMB_COLOR, thumb_rect, border_radius=6)
    else:
        # Draw disabled track (content fits)
        pygame.draw.rect(screen, (240, 240, 240), track_rect, border_radius=6)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()


