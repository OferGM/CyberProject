import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1580, 1000
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
FONT = pygame.font.Font(None, 36)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape from Tarkov Login")

# Load background image
background = pygame.image.load("LoginPageBackground.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load images
login_butt_img = pygame.image.load("LoginButt.png").convert_alpha()

# Custom Button class
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

# Main loop
def login_page():
    username = ""
    password = ""
    is_typing_username = True

    login_button = Button(200, 750, login_butt_img)
    login_button1 = Button(1000, 750, login_butt_img)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    is_typing_username = not is_typing_username
                elif event.key == pygame.K_RETURN:
                    if is_typing_username:
                        is_typing_username = False
                    else:
                        # Perform login validation here
                        print("Logging in with:")
                        print("Username:", username)
                        print("Password:", password)

                elif event.key == pygame.K_BACKSPACE:
                    if is_typing_username:
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    if is_typing_username:
                        username += event.unicode
                    else:
                        password += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_button.rect.collidepoint(event.pos):
                    # Perform login validation here
                    print("Logging in with:")
                    print("Username:", username)
                    print("Password:", password)

        # Draw background
        screen.blit(background, (0, 0))

        # Draw login elements
        login_button.draw()
        login_button1.draw()

        pygame.draw.rect(screen, GRAY, (250, 250, 300, 50))  # Username box
        pygame.draw.rect(screen, GRAY, (250, 320, 300, 50))  # Password box

        text_surface = FONT.render("Username:", True, (0, 0, 0))
        screen.blit(text_surface, (150, 250))

        text_surface = FONT.render("Password:", True, (0, 0, 0))
        screen.blit(text_surface, (150, 320))

        if is_typing_username:
            pygame.draw.rect(screen, (0, 0, 0), (260 + FONT.size(username)[0], 260, 2, 30))
        else:
            pygame.draw.rect(screen, (0, 0, 0), (260 + FONT.size(password)[0], 330, 2, 30))

        if is_typing_username:
            text_surface = FONT.render(username, True, (0, 0, 0))
            screen.blit(text_surface, (260, 260))
        else:
            masked_password = "*" * len(password)
            text_surface = FONT.render(masked_password, True, (0, 0, 0))
            screen.blit(text_surface, (260, 330))

        pygame.display.flip()

# Run the login page
login_page()
