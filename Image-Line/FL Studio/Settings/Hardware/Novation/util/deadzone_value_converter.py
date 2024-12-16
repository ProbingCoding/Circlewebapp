class DeadzoneValueConverter:

    def __init__(self, max, centre, width):
        self.max = max
        self.deadzone_centre = centre
        self.deadzone_lower = centre - width / 2
        self.deadzone_upper = centre + width / 2
        self.upper_scalar = (self.max - self.deadzone_centre) / (self.max - self.deadzone_upper)
        self.lower_scalar = self.deadzone_centre / self.deadzone_lower

    def __call__(self, value):
        if value >= self.deadzone_upper:
            return (value - self.deadzone_upper) * self.upper_scalar + self.deadzone_centre

        if value > self.deadzone_lower:
            return self.deadzone_centre

        return value * self.lower_scalar
