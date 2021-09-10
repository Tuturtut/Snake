import random
import sys
import pygame
from pygame.locals import *
from color import *

pygame.mixer.init()
start_sound = pygame.mixer.Sound(r'sound\start_sound.wav')
died_sound = pygame.mixer.Sound(r'sound\died_sound.wav')
eat_apple_sound = pygame.mixer.Sound(r'sound\eat_apple_sound.wav')
menu_move_sound = pygame.mixer.Sound(r'sound\menu_move_sound.wav')
snake_move_sound = pygame.mixer.Sound(r'sound\snake_move_sound.wav')
pause_sound = pygame.mixer.Sound(r'sound\pause_sound.wav')


class Game:
	start = True
	score = 0
	last_color = GREEN
	color_choice = 1
	speed_choice = 1
	sound_choice = 0

	def __init__(self):
		self.pause_state = 0
		self.color_choice = Game.color_choice
		self.choice = 0
		self.sound_choice = Game.sound_choice
		self.color = Game.last_color
		self.color1 = self.color[0]  # sombre
		self.color2 = self.color[1]  # clair
		self.text_game_speed_color = self.color1
		self.text_game_color_color = self.color1
		self.text_sound_color = self.color1
		self.sound_actived = False

		self.speed_state = Game.speed_choice
		self.turn_pause = 0
		self.on_pause = False
		self.defeat = False
		self.window_x = 600
		self.window_y = 600
		self.logo = pygame.image.load(r'image\Snake_Logo-1.png')
		pygame.display.set_icon(self.logo)
		pygame.display.set_caption("Snake")
		self.window = pygame.display.set_mode((self.window_x, self.window_y))

		self.snake_x_pos = 300
		self.snake_y_pos = 300
		self.snake_x_start_pos = self.snake_x_pos
		self.snake_y_start_pos = self.snake_y_pos
		self.snake_x_direction = 0
		self.snake_y_direction = 0
		self.snake_body = 20
		self.has_turn = False

		with open('Snake_Score.txt', 'r+') as score_file:
			self.best_score = int(score_file.readline())

			score_file.close()

		WALL_SIZE = 10
		self.wall_left = WALL_SIZE * self.snake_body
		self.wall_up = WALL_SIZE * self.snake_body
		self.size_x = 2 * WALL_SIZE * self.snake_body
		self.size_y = 2 * WALL_SIZE * self.snake_body

		self.apple_pos_x = random.randrange(self.snake_x_start_pos - self.wall_left,
		                                    self.snake_x_start_pos + self.wall_left - self.snake_body,
		                                    self.snake_body)
		self.apple_pos_y = random.randrange(self.snake_y_start_pos - self.wall_up,
		                                    self.snake_y_start_pos + self.wall_up - self.snake_body,
		                                    self.snake_body)

		self.snake_positions = []

		self.snake_size = 2

		self.cheat_activate = False

		self.start_screen = True

		self.START_FPS = 6
		self.fps = self.START_FPS

		self.clock = pygame.time.Clock()

	def main(self):
		on_game = True
		while on_game:

			self.__init__()

			self.start_screen_display()

			self.create_message('moyenne', f'Press space to start', (200, 25, 200, 5), (255, 255, 255))

			self.draw_start_screen()

			Game.score = 0
			while not self.defeat:
				Game.start = False
				while self.on_pause:
					self.start_pause_screen_display()
					pygame.display.flip()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						quit()

					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
							if self.turn_pause == 0:
								self.on_pause = True
								self.turn_pause = 1
								if self.sound_actived:
									pause_sound.play()
								break
						if not self.has_turn:
							if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
								if self.snake_x_direction != -self.snake_body or self.cheat_activate:
									self.snake_x_direction = self.snake_body
									self.snake_y_direction = 0
									self.has_turn = True

							elif event.key == pygame.K_q or event.key == pygame.K_LEFT:
								if self.snake_x_direction != self.snake_body or self.cheat_activate:
									self.snake_x_direction = -self.snake_body
									self.snake_y_direction = 0
									self.has_turn = True

							elif event.key == pygame.K_z or event.key == pygame.K_UP:
								if self.snake_y_direction != self.snake_body or self.cheat_activate:
									self.snake_x_direction = 0
									self.snake_y_direction = -self.snake_body
									self.has_turn = True

							elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
								if self.snake_y_direction != -self.snake_body or self.cheat_activate:
									self.snake_x_direction = 0
									self.snake_y_direction = self.snake_body
									self.has_turn = True

				# s'il sort de la zone
				if self.snake_x_pos < self.snake_x_start_pos - self.wall_left:
					self.defeat = True
					if self.sound_actived:
						died_sound.play()
					break

				if self.snake_y_pos < self.snake_y_start_pos - self.wall_up:
					self.defeat = True
					if self.sound_actived:
						died_sound.play()
					break

				if self.snake_x_pos > self.snake_x_start_pos + self.wall_left - self.snake_body - 10:
					self.defeat = True
					if self.sound_actived:
						died_sound.play()
					break

				if self.snake_y_pos > self.snake_y_start_pos + self.wall_up - self.snake_body - 10:
					self.defeat = True
					if self.sound_actived:
						died_sound.play()
					break

				self.movement()
				if self.has_turn and self.sound_actived:
					snake_move_sound.play()
				self.has_turn = False

				# Tester s'il touche la pomme
				if self.apple_pos_x == self.snake_x_pos and self.apple_pos_y == self.snake_y_pos:
					self.apple_pos_x = random.randrange(self.snake_x_start_pos - self.wall_left,
					                                    self.snake_x_start_pos + self.wall_left - self.snake_body,
					                                    self.snake_body)
					self.apple_pos_y = random.randrange(self.snake_y_start_pos - self.wall_up,
					                                    self.snake_y_start_pos + self.wall_up - self.snake_body,
					                                    self.snake_body)
					collision = True
					while collision:
						# Randomizing the apple position
						self.apple_pos_x = random.randrange(self.snake_x_start_pos - self.wall_left,
						                                    self.snake_x_start_pos + self.wall_left - self.snake_body,
						                                    self.snake_body)
						self.apple_pos_y = random.randrange(self.snake_y_start_pos - self.wall_up,
						                                    self.snake_y_start_pos + self.wall_up - self.snake_body,
						                                    self.snake_body)
						# Check apple not within snake
						collision = False
						for snake_part in self.snake_positions:
							part = pygame.Rect(snake_part[0], snake_part[1], self.snake_body, self.snake_body)
							# is the apple-point within the snake part?
							if part.collidepoint(self.apple_pos_x, self.apple_pos_y):
								collision = True
								break  # any collision is final, stop checking

					# augmenter la taille du serpent
					self.snake_size += 1
					if self.sound_actived:
						eat_apple_sound.play()
					Game.score += 1
					with open(r'Snake_Score.txt', 'r+') as score_file:
						if Game.score > self.best_score and not self.cheat_activate:
							score_file.close()
							with open(r'Snake_Score.txt', 'w+') as score_file:
								score_file.write(str(Game.score))
								score_file.close()

				snake_head = [self.snake_x_pos, self.snake_y_pos]

				self.snake_positions.append(snake_head)

				if len(self.snake_positions) > self.snake_size:
					self.snake_positions.pop(0)

				if not self.cheat_activate:
					self.bite_oneself(snake_head)

				self.draw()

				if self.turn_pause != 1:
					pygame.display.flip()

				self.clock.tick(self.fps)

	def create_wall(self):
		border_size = self.snake_body
		spacement = border_size / 2
		wall_color = self.color1
		min_x = self.snake_x_start_pos - self.wall_left - spacement - 1
		min_y = self.snake_y_start_pos - self.wall_up - spacement - 1
		size_x = self.size_x + 1
		size_y = self.size_y + 1
		snake_map = Rect(min_x, min_y, size_x, size_y)

		pygame.draw.rect(self.window, wall_color, snake_map, border_size)

	def movement(self):
		self.snake_x_pos += self.snake_x_direction
		self.snake_y_pos += self.snake_y_direction

	def draw_apple(self, x, y, size, color):
		size = size / 3
		rect1 = Rect(x, y + size, size, size)
		rect2 = Rect(x + size, y, size, size)
		rect3 = Rect(x + size, y + 2 * size, size, size)
		rect4 = Rect(x + 2 * size, y + size, size, size)
		pygame.draw.rect(self.window, color, rect1)
		pygame.draw.rect(self.window, color, rect2)
		pygame.draw.rect(self.window, color, rect3)
		pygame.draw.rect(self.window, color, rect4)

	def create_message(self, font, message, rect_message, color):

		if font == 'petite':
			font = pygame.font.SysFont('Heather', 20, False)

		elif font == 'moyenne':
			font = pygame.font.SysFont('Heather', 30, False)

		elif font == 'grande':
			font = pygame.font.SysFont('Heather', 60, False)

		elif font == 'enorme':
			font = pygame.font.SysFont('Heather', 130, False)

		message = font.render(message, True, color)

		self.window.blit(message, rect_message)

	def draw_snake(self):
		snake_color = self.color1

		# afficher le serpent
		for snake_part in self.snake_positions:
			pygame.draw.rect(self.window, snake_color, (snake_part[0], snake_part[1], self.snake_body, self.snake_body))

	def draw(self):
		bg_color = self.color2
		text_color = self.color1
		apple_color = self.color1

		self.window.fill(bg_color)

		# afficher le mur
		self.create_wall()

		self.draw_apple(self.apple_pos_x, self.apple_pos_y, self.snake_body, apple_color)

		self.create_message('moyenne', f'Best Score : {self.best_score}', (215, 520, 200, 5), text_color)
		self.create_message('moyenne', f'Score : {Game.score}', (240, 550, 200, 5), text_color)
		self.create_message('grande', 'Snake', (225, 20, 200, 5), text_color)

		# afficher le serpent
		self.draw_snake()

		if self.is_cheat_activate():
			self.create_message('petite', 'Cheat Active', (10, 550, 200, 5), text_color)

	def draw_start_screen(self):
		bg_color = self.color2
		text_color = self.color1

		self.window.fill(bg_color)

		# afficher le mur
		self.create_wall()

		# afficher le serpent
		self.draw_snake()

		self.create_message('enorme', 'Snake', (150, 150, 200, 5), text_color)
		if Game.start:
			self.create_message('moyenne', f'Best Score : {self.best_score}', (215, 260, 200, 5), text_color)
		else:
			self.create_message('moyenne', f'Your Score : {Game.score}', (215, 240, 200, 5), text_color)
			self.create_message('moyenne', f'Best Score : {self.best_score}', (215, 270, 200, 5), text_color)

		self.create_message('moyenne', 'Press Space to Start', (185, 535, 200, 5), text_color)

		self.create_message('petite', 'Game Speed', (250, 300, 200, 5), text_color)
		dark_color_rect = Rect((190, 320, 200, 30))
		pygame.draw.rect(self.window, text_color, dark_color_rect)

		self.create_message('petite', 'Game Color', (253, 360, 200, 5), text_color)
		dark_color_rect = Rect((190, 380, 200, 30))
		pygame.draw.rect(self.window, text_color, dark_color_rect)

		self.create_message('petite', 'Sound', (269, 420, 200, 5), text_color)
		dark_color_rect = Rect((190, 440, 200, 30))
		pygame.draw.rect(self.window, text_color, dark_color_rect)

		if self.choice == 0:
			self.text_game_color_color = self.color2
			self.text_game_speed_color = self.color1
			self.text_sound_color = self.color2

			light_color_rect = Rect((200, 325, 180, 20))
			pygame.draw.rect(self.window, bg_color, light_color_rect)

		elif self.choice == 1:  # text color
			self.text_game_color_color = self.color1
			self.text_game_speed_color = self.color2
			self.text_sound_color = self.color2

			light_color_rect = Rect((200, 385, 180, 20))
			pygame.draw.rect(self.window, bg_color, light_color_rect)

		elif self.choice == 2:
			self.text_game_color_color = self.color2
			self.text_game_speed_color = self.color2
			self.text_sound_color = self.color1

			light_color_rect = Rect((200, 445, 180, 20))
			pygame.draw.rect(self.window, bg_color, light_color_rect)

		if self.start_screen_control() == 0:
			self.create_message('petite', 'Slow', (275, 328, 100, 15), self.text_game_speed_color)
			self.START_FPS = 5
			Game.speed_choice = 0
		elif self.start_screen_control() == 1:
			self.create_message('petite', 'Medium', (265, 328, 100, 15), self.text_game_speed_color)
			self.START_FPS = 7
			Game.speed_choice = 1
		elif self.start_screen_control() == 2:
			self.create_message('petite', 'Fast', (277, 328, 100, 15), self.text_game_speed_color)
			self.START_FPS = 11
			Game.speed_choice = 2
		self.fps = self.START_FPS

		if self.color_choice == 0:
			self.create_message('petite', 'Red', (277, 388, 100, 15), self.text_game_color_color)
			self.color = RED
			Game.last_color = RED
			Game.color_choice = 0
		if self.color_choice == 1:
			self.create_message('petite', 'Green', (270, 388, 100, 15), self.text_game_color_color)
			self.color = GREEN
			Game.last_color = GREEN
			Game.color_choice = 1
		if self.color_choice == 2:
			self.create_message('petite', 'Blue', (275, 388, 100, 15), self.text_game_color_color)
			self.color = BLUE
			Game.last_color = BLUE
			Game.color_choice = 2
		if self.color_choice == 3:
			self.create_message('petite', 'Pink', (275, 388, 100, 15), self.text_game_color_color)
			self.color = PINK
			Game.last_color = PINK
			Game.color_choice = 3
		if self.color_choice == 4:
			self.create_message('petite', 'Yellow', (269, 388, 100, 15), self.text_game_color_color)
			self.color = YELLOW
			Game.last_color = YELLOW
			Game.color_choice = 4
		if self.color_choice == 5:
			self.create_message('petite', 'Orange', (269, 388, 100, 15), self.text_game_color_color)
			self.color = ORANGE
			Game.last_color = ORANGE
			Game.color_choice = 5

		if self.sound_choice == 0:
			self.create_message('petite', 'Off', (280, 448, 100, 15), self.text_sound_color)
			self.sound_actived = False
			Game.sound_choice = 0
		elif self.sound_choice == 1:
			self.create_message('petite', 'On', (280, 448, 100, 15), self.text_sound_color)
			self.sound_actived = True
			Game.sound_choice = 1

		self.color1 = self.color[0]  # sombre
		self.color2 = self.color[1]  # clair

		if self.is_cheat_activate():
			self.create_message('petite', 'Cheat Active', (10, 550, 200, 5), text_color)
		pygame.display.flip()

	def bite_oneself(self, snake_head):
		# Si le serpent se 'mord' le jeu s'arrete
		for snake_part in self.snake_positions[:-2]:
			if snake_head == snake_part:
				if self.sound_actived:
					died_sound.play()
				self.defeat = True

	def is_cheat_activate(self):
		if self.cheat_activate:
			return True
		elif self.cheat_activate is False:
			return False

	def draw_pause(self):
		bg_color = self.color2
		text_color = self.color1

		self.window.fill(bg_color)

		self.create_wall()

		self.create_message('enorme', 'Pause', (155, 150, 200, 5), text_color)

		dark_color_rect = Rect((190, 340, 200, 30))
		pygame.draw.rect(self.window, text_color, dark_color_rect)

		dark_color_rect = Rect((190, 410, 200, 30))
		pygame.draw.rect(self.window, text_color, dark_color_rect)

		if self.pause_state == 1:
			self.text_game_color_color = self.color2
			self.text_game_speed_color = self.color1

			light_color_rect = Rect((200, 415, 180, 20))
			pygame.draw.rect(self.window, bg_color, light_color_rect)

		elif self.pause_state == 0:  # text color
			self.text_game_color_color = self.color1
			self.text_game_speed_color = self.color2
			light_color_rect = Rect((200, 345, 180, 20))
			pygame.draw.rect(self.window, bg_color, light_color_rect)

		if self.is_cheat_activate():
			self.create_message('petite', 'Cheat Active', (10, 550, 200, 5), text_color)

		self.create_message('petite', 'Resume', (265, 348, 200, 5), self.text_game_color_color)

		self.create_message('petite', 'Give Up', (265, 418, 200, 5), self.text_game_speed_color)

		pygame.display.flip()

	def pause_controle(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
					if self.turn_pause == 1:
						if self.pause_state == 0:
							self.on_pause = False
							self.turn_pause = 0
							if self.sound_actived:
								start_sound.play()
						elif self.pause_state == 1:
							self.defeat = True
							self.on_pause = False
				if event.key == pygame.K_DOWN or event.key == pygame.K_s:
					self.pause_state -= 1
					if self.sound_actived:
						menu_move_sound.play()
				if event.key == pygame.K_ESCAPE or event.key == pygame.K_END:
					quit()

				if event.key == pygame.K_UP or event.key == pygame.K_z:
					self.pause_state += 1
					if self.sound_actived:
						menu_move_sound.play()

				if self.pause_state > 1:
					self.pause_state = 0
				if self.pause_state < 0:
					self.pause_state = 1

	def start_pause_screen_display(self):
		self.pause_controle()

		self.draw_pause()

		pygame.display.flip()

	def active_cheat(self):
		if self.cheat_activate:
			self.cheat_activate = False
		elif self.cheat_activate is False:
			self.cheat_activate = True

	def start_screen_control(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.KEYDOWN:

				if event.key == pygame.K_s or event.key == pygame.K_DOWN:
					self.choice += 1
					if self.sound_actived:
						menu_move_sound.play()
				if event.key == pygame.K_z or event.key == pygame.K_UP:
					self.choice -= 1
					if self.sound_actived:
						menu_move_sound.play()
				if self.choice > 2:
					self.choice = 0
				if self.choice < 0:
					self.choice = 2

				if self.choice == 0:
					if event.key == pygame.K_d or event.key == K_RIGHT:
						self.speed_state += 1
						if self.sound_actived:
							menu_move_sound.play()
					if event.key == pygame.K_q or event.key == K_LEFT:
						self.speed_state -= 1
						if self.sound_actived:
							menu_move_sound.play()
					if self.speed_state >= 3:
						self.speed_state = 0
					if self.speed_state < 0:
						self.speed_state = 2

				if self.choice == 1:
					if event.key == pygame.K_d or event.key == K_RIGHT:
						self.color_choice += 1
						if self.sound_actived:
							menu_move_sound.play()
					if event.key == pygame.K_q or event.key == K_LEFT:
						self.color_choice -= 1
						if self.sound_actived:
							menu_move_sound.play()
					if self.color_choice > 5:
						self.color_choice = 0
					if self.color_choice < 0:
						self.color_choice = 5

				if self.choice == 2:
					if event.key == pygame.K_d or event.key == K_RIGHT:
						self.sound_choice += 1
						if not self.sound_actived:
							menu_move_sound.play()
					if event.key == pygame.K_q or event.key == K_LEFT:
						self.sound_choice -= 1
						if not self.sound_actived:
							menu_move_sound.play()
					if self.sound_choice > 1:
						self.sound_choice = 0
					if self.sound_choice < 0:
						self.sound_choice = 1

				if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
					self.start_screen = False
					if self.sound_actived:
						start_sound.play()
				if event.key == pygame.K_c:
					self.active_cheat()
					if self.sound_actived:
						menu_move_sound.play()
				if event.key == pygame.K_ESCAPE or event.key == pygame.K_END:
					quit()
		return self.speed_state

	def start_screen_display(self):
		while self.start_screen:
			self.start_screen_control()

			self.draw_start_screen()

			pygame.display.flip()


if __name__ == '__main__':
	pygame.init()
	Game().main()
	pygame.quit()