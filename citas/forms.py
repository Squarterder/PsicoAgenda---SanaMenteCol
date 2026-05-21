from django import forms
from django.contrib.auth import authenticate
from .models import Cita, SeguimientoClinico, Usuario


class FormularioLogin(forms.Form):
    usuario = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre de usuario', 'autocomplete': 'username'}),
    )
    contrasena = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={'placeholder': '...', 'autocomplete': 'current-password'}),
    )

    def clean(self):
        datos = super().clean()
        usuario_nombre = datos.get('usuario')
        contrasena = datos.get('contrasena')

        if usuario_nombre and contrasena:
            usuario = authenticate(username=usuario_nombre, password=contrasena)
            if usuario is None:
                raise forms.ValidationError('Usuario o contrasena incorrectos.')
            if not usuario.habilitado:
                raise forms.ValidationError('Tu cuenta esta deshabilitada. Contacta al administrador.')
            datos['usuario_obj'] = usuario
        return datos


class FormularioRegistro(forms.ModelForm):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: juan123 (sin espacios)'}),
    )
    contrasena = forms.CharField(
        label='Contrasena',
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Minimo 6 caracteres'}),
    )
    confirmar_contrasena = forms.CharField(
        label='Confirmar contrasena',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contrasena'}),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidos', 'correo', 'celular']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Tus apellidos'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'tucorreo@ejemplo.com'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Ej: 3001234567'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if ' ' in username:
            raise forms.ValidationError('El nombre de usuario no puede contener espacios.')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya esta en uso. Elige otro.')
        return username

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return correo

    def clean(self):
        datos = super().clean()
        c1 = datos.get('contrasena')
        c2 = datos.get('confirmar_contrasena')
        if c1 and c2 and c1 != c2:
            raise forms.ValidationError('Las contrasenas no coinciden.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['username']
        usuario.email = self.cleaned_data['correo']
        usuario.rol = 'paciente'
        usuario.habilitado = True
        usuario.set_password(self.cleaned_data['contrasena'])
        if commit:
            usuario.save()
        return usuario


class FormularioCrearUsuario(forms.ModelForm):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: juan123 (sin espacios)'}),
    )
    contrasena = forms.CharField(
        label='Contrasena',
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Minimo 6 caracteres'}),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidos', 'correo', 'celular', 'rol']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Ej: 3001234567'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if ' ' in username:
            raise forms.ValidationError('El nombre de usuario no puede contener espacios.')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya esta en uso. Elige otro.')
        return username

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return correo

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['username']
        usuario.email = self.cleaned_data['correo']
        usuario.habilitado = True
        usuario.set_password(self.cleaned_data['contrasena'])
        if commit:
            usuario.save()
        return usuario


class FormularioEditarUsuario(forms.ModelForm):
    contrasena_nueva = forms.CharField(
        label='Nueva contrasena (dejar en blanco para no cambiar)',
        required=False,
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Dejar en blanco para no cambiar'}),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidos', 'correo', 'celular', 'rol', 'habilitado']
        widgets = {
            'nombre': forms.TextInput(),
            'apellidos': forms.TextInput(),
            'correo': forms.EmailInput(),
            'celular': forms.TextInput(),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        qs = Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return correo

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['correo']
        nueva = self.cleaned_data.get('contrasena_nueva')
        if nueva:
            usuario.set_password(nueva)
        if commit:
            usuario.save()
        return usuario


class FormularioReservarCita(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe brevemente el motivo de tu consulta (opcional)',
            }),
        }


class FormularioSeguimiento(forms.ModelForm):
    class Meta:
        model = SeguimientoClinico
        fields = ['notas', 'diagnostico_preliminar', 'proxima_accion']
        widgets = {
            'notas': forms.Textarea(attrs={
                'rows': 7,
                'placeholder': 'Anota observaciones clinicas, evolucion del paciente, temas tratados en sesion...',
            }),
            'diagnostico_preliminar': forms.TextInput(attrs={
                'placeholder': 'Ej: Trastorno de ansiedad generalizada (provisional)',
            }),
            'proxima_accion': forms.TextInput(attrs={
                'placeholder': 'Ej: Aplicar tecnica de respiracion diafragmatica en proxima sesion',
            }),
        }


class FormularioCancelarCita(forms.Form):
    motivo_cancelacion = forms.CharField(
        label='Motivo de cancelacion',
        min_length=10,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Explica brevemente el motivo por el cual cancelas esta cita. El paciente recibira este mensaje.',
        }),
    )
