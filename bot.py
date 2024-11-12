# src/bot.py

import os

from controllers.battle_controller import BattleController
from controllers.emulator_controller import EmulatorController
from controllers.game_controller import GameController
from models.game_state import GameState
from services.card_data_service import CardDataService
from services.card_recognition_service import CardRecognitionService
from utils.image_utils import ImageProcessor
from utils.loaders import load_all_cards, load_template_images


class PokemonBot:
    def __init__(self, app_state, log_callback, ui_instance):
        self.app_state = app_state
        self.log_callback = log_callback
        self.ui_instance = ui_instance

        self.template_images = load_template_images("images")
        images_cards_folder = "images/cards"
        if not os.path.exists(images_cards_folder):
            os.makedirs(images_cards_folder)
        self.card_images = load_all_cards(images_cards_folder)

        self.card_data_service = CardDataService()
        self.image_processor = ImageProcessor(self.log_callback)
        self.battle_controller = BattleController(
            self.image_processor,
            self.template_images,
            self.card_images,
            self.log_callback,
        )

        self.game_state = GameState()
        self.emulator_controller = EmulatorController(self.app_state, self.log_callback)
        self.card_recognition_service = CardRecognitionService(
            self.image_processor,
            self.card_data_service,
            self.ui_instance,
            self.log_callback,
            self.card_images,
        )

        self.game_controller = GameController(
            self.app_state,
            self.emulator_controller,
            self.battle_controller,
            self.image_processor,
            self.card_recognition_service,
            self.game_state,
            self.template_images,
            self.log_callback,
        )

    def start(self):
        self.game_controller.start()

    def stop(self):
        self.game_controller.stop()
