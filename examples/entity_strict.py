from dataclasses import dataclass


def entity_strict(cls):
    """
    Строгий декоратор для сущностей — запрещает создание новых атрибутов
    Не добавляю, потому что это замедлит код.
    Может быть полезно при отладке

    Strict decorator for entities — prohibits the creation of new attributes
    I'm not adding it because it will slow down the code.
    May be useful when debugging
    """
    # Применяем dataclass со слотами
    cls = dataclass(cls, slots=True)  # noqa
    # Явно задаём пустые слоты, если их нет
    if not hasattr(cls, '__slots__'):
        cls.__slots__ = ()

    # Переопределяем __setattr__, чтобы запретить новые атрибуты
    def __setattr__(self, name, value):
        if hasattr(self, name) or name in self.__slots__:
            # Разрешаем менять существующие атрибуты
            super(cls, self).__setattr__(name, value)
        else:
            raise AttributeError(f"Cannot add new attribute '{name}' to entity {self.__class__.__name__}")

    cls.__setattr__ = __setattr__

    return cls
