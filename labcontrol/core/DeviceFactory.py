#zie https://realpython.com/factory-method-python/
#omdat overerving in python toch anders werkt dan C# of Java, geeft artikel een werkwijze

#idee artikel: een serializer
#Begin bovenin de boom:

#class SerializerFactory:
#    def get_serializer(self, format):
#        if format == 'JSON':
#            return JsonSerializer()
#        elif format == 'XML':
#            return XmlSerializer()
#        else:
#            raise ValueError(format)

# JsonSerializer en XmlSerializer hebben eenzelfde onderliggende interface als JsonSerializer:
#

#class JsonSerializer:
#    def __init__(self):
#        self._current_object = None
#
#    def start_object(self, object_name, object_id):
#        self._current_object = {
#            'id': object_id
#        }
#
#    def add_property(self, name, value):
#        self._current_object[name] = value
#
#    def to_str(self):
#        return json.dumps(self._current_object)

# Om de boel aan elkaar te plakken beschrijft dit artikel de bovenliggende generieke interface, in dit geval is dat:
#class ObjectSerializer:
#    def serialize(self, serializable, format):
#        serializer = factory.get_serializer(format)
#        serializable.serialize(serializer)
#        return serializer.to_str()

# Het artikel noemt een aantal interessante zaken.
#The Serializer interface is an abstract concept due to the dynamic nature of the Python language. 
# Static languages like Java or C# require that interfaces be explicitly defined. In Python, any object that provides the desired methods 
# or functions is said to implement the interface. The example defines the Serializer interface to be an object that implements the 
# following methods or functions:
#
#    .start_object(object_name, object_id)
#    .add_property(name, value)
#    .to_str()

#This interface is implemented by the concrete classes JsonSerializer and XmlSerializer.