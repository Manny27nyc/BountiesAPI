import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from notifications.constants import default_email_options, notifications


class Language(models.Model):
    name = models.CharField(max_length=128, unique=True)
    normalized_name = models.CharField(max_length=128)
    native_name = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.normalized_name = self.name.lower().strip()
        super(Language, self).save(*args, **kwargs)


class Skill(models.Model):
    name = models.CharField(max_length=128, unique=True)
    normalized_name = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.normalized_name = self.name.lower().strip()
        super(Skill, self).save(*args, **kwargs)


class Settings(models.Model):
    emails = JSONField(null=False, default=default_email_options)

    def readable_accepted_email_settings(self):
        merged_settings = {
            **self.emails['issuer'],
            **self.emails['both'],
            **self.emails['fulfiller']}
        return [setting for setting in merged_settings if merged_settings[setting]]

    def accepted_email_settings(self):
        merged_settings = {
            **self.emails['issuer'],
            **self.emails['both'],
            **self.emails['fulfiller']}
        return [notifications[setting]
                for setting in merged_settings if merged_settings[setting]]


class User(models.Model):
    profile_hash = models.CharField(max_length=128, blank=True)
    public_address = models.TextField(max_length=500, blank=True, unique=True)
    nonce = models.UUIDField(default=uuid.uuid4, null=False, blank=False)
    categories = models.ManyToManyField('std_bounties.Category')
    name = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=128, blank=True)
    organization = models.CharField(max_length=128, blank=True)
    languages = models.ManyToManyField('user.Language')
    skills = models.ManyToManyField('user.Skill')
    profileFileName = models.CharField(max_length=256, blank=True)
    profileFileHash = models.CharField(max_length=256, blank=True)
    profileDirectoryHash = models.CharField(max_length=256, blank=True)
    profile_image = models.CharField(max_length=256, blank=True)
    website = models.CharField(max_length=128, blank=True)
    twitter = models.CharField(max_length=128, blank=True)
    github = models.CharField(max_length=128, blank=True)
    linkedin = models.CharField(max_length=128, blank=True)
    dribble = models.CharField(max_length=128, blank=True)
    github_username = models.CharField(max_length=128, blank=True)
    settings = models.ForeignKey(Settings, null=True)

    def save(self, *args, **kwargs):
        if not self.settings:
            self.settings = Settings.objects.create()
        super(User, self).save(*args, **kwargs)

    def save_and_clear_skills(self, skills):
        # this is really messy, but this is bc of psql django bugs
        self.skills.clear()
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, str):
                    try:
                        matching_skill = Skill.objects.get(
                            normalized_name=skill.strip().lower())
                        self.skills.add(matching_skill)
                    except ObjectDoesNotExist:
                        self.skills.create(name=skill.strip())

    def save_and_clear_languages(self, languages):
        # this is really messy, but this is bc of psql django bugs
        self.languages.clear()
        if isinstance(languages, list):
            for language in languages:
                if isinstance(language, str):
                    try:
                        matching_language = Language.objects.get(
                            normalized_name=language.strip().lower())
                        self.languages.add(matching_language)
                    except ObjectDoesNotExist:
                        pass