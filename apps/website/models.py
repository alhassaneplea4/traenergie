from django.db import models


class Service(models.Model):
    ICON_CHOICES = [
        ("bolt", "Éclairage & Énergie"),
        ("cpu", "Automatisation"),
        ("shield", "Sécurité Électrique"),
        ("tool", "Maintenance"),
        ("zap", "Installation"),
        ("activity", "Audit Énergétique"),
    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default="bolt")
    title = models.CharField(max_length=150)
    description = models.TextField()
    detail_content = models.TextField(
        blank=True,
        verbose_name="Contenu détaillé",
        help_text="Description longue affichée sur la page détail. Chaque ligne vide crée un nouveau paragraphe.",
    )
    image = models.ImageField(upload_to="services/", blank=True, null=True, verbose_name="Image")
    color = models.CharField(max_length=20, default="cyan")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("installation", "Installation"),
        ("maintenance", "Maintenance"),
        ("audit", "Audit"),
        ("equipement", "Équipement"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    client = models.CharField(max_length=200, blank=True)
    completion_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Membre d'équipe"
        verbose_name_plural = "Équipe"

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    author_name = models.CharField(max_length=150)
    author_company = models.CharField(max_length=150, blank=True)
    author_image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"

    def __str__(self):
        return f"{self.author_name} — {self.author_company}"


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ("new", "Nouveau"),
        ("read", "Lu"),
        ("replied", "Répondu"),
        ("closed", "Clôturé"),
    ]
    name = models.CharField(max_length=150, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.name} — {self.subject}"


class CompanyInfo(models.Model):
    """Singleton model — one row only."""
    name = models.CharField(max_length=200, default="Traenergie")
    tagline = models.CharField(max_length=300, default="Votre expert en solutions électriques")
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    years_experience = models.PositiveIntegerField(default=10)
    projects_count = models.PositiveIntegerField(default=500)
    clients_count = models.PositiveIntegerField(default=200)
    technicians_count = models.PositiveIntegerField(default=50)

    class Meta:
        verbose_name = "Informations entreprise"
        verbose_name_plural = "Informations entreprise"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
