from rest_framework import serializers
from .models import Event
from locations.models import Location
from services.models import Service
from packages.models import Package

class LocationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'address')

class ServiceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name')

class PackageSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('id', 'name')

class EventSerializer(serializers.ModelSerializer):
    # Para leer locación y servicios como objetos
    location = LocationSimpleSerializer(read_only=True)
    services = ServiceSimpleSerializer(many=True, read_only=True)
    package = PackageSimpleSerializer(read_only=True)

    # Para escribir con IDs
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True
    )
    # Campos opcionales según el tipo de evento (paquete o servicios)
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, source='services', 
        write_only=True, required=False
    )
    
    package_id = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(), source='package', 
        write_only=True, required=False
    )


    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'location', 'location_id',
            'is_package',  # Nuevo campo
            'services', 'service_ids',
            'package', 'package_id',
            'status', 'image',
            'created_at', 'updated_at', 'company'  # <- Añadido aquí
        ]
        read_only_fields = ('created_at', 'updated_at', 'company')

    def validate(self, data):
            location = data['location']
            start = data['start_date']
            end = data['end_date']

            event_id = self.instance.id if self.instance else None

            # Verificar solapamiento en esa locación y empresa
            overlapping_events = Event.objects.filter(
                location=location,
                start_date__lt=end,
                end_date__gt=start
            ).exclude(id=event_id)

            if overlapping_events.exists():
                raise serializers.ValidationError(
                    "Ya existe un evento programado en esta locación para esas fechas."
                )

            # Validar que la locación pertenezca a la misma empresa del usuario
            request = self.context.get('request')
            if request and request.user.company != location.company:
                raise serializers.ValidationError("No puedes usar una locación de otra empresa.")

            return data
  #  def validate(self, data):
    """
    Validar que se proporcione package o services según el valor de is_package
    """
   #     is_package = data.get('is_package', False)
        
    #    if is_package:
    #        if 'package' not in data:
     #           raise serializers.ValidationError(
     #               "Debe proporcionar un package_id cuando is_package es True"
     #           )
     #   else:
     #       if 'services' not in data or not data['services']:
     #           raise serializers.ValidationError(
     #               "Debe proporcionar service_ids cuando is_package es False"
     #           )
     #   
     #   return data
