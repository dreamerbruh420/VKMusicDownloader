#!/usr/bin/python3
# -*- coding: utf-8 -*-

from math import ceil

from vkapi import VKLight, VKLightError
from vkapi import receipt


class APIConstants:
	count_audios = 200


class APIHandler:
	""" Класс реализующий логику работы с api"""
	
	def __init__(self, api: VKLight):
		self.api = api

	def refresh_token(self, access_token) -> dict:
		"""Метод обновляющий access_token"""
		try:
			return self.api.call("auth.refreshToken", {
				"access_token": access_token,
				"receipt": receipt
			})
		except VKLightError as e:
			raise e

	def get_audio(self, user_id, count=None, offset=0) -> dict:
		"""Получение списка аудиозаписей"""
		try:
			return self.api.call("audio.get", {
				"user_id": user_id,
				"count": count,
				"offset": offset
			})
		except VKLightError as e:
			raise e

	def get_count_audio(self, user_id) -> int:
		"""Количество аудиозаписей"""
		try:
			return self.api.call("audio.get", {
				"user_id": user_id,
				"count": 0
			})['response']['count']
		except VKLightError as e:
			raise e
