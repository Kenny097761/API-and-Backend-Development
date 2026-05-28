class Shipment:
    def __init__(
        self,
        shipment_id,
        order_id,
        staff_id,
        status,
        street_number,
        street_name,
        suburb,
        postcode,
        created_at,
        staff_name=None,
    ):
        self.shipment_id = shipment_id
        self.order_id = order_id
        self.staff_id = staff_id
        self.status = status
        self.street_number = street_number
        self.street_name = street_name
        self.suburb = suburb
        self.postcode = postcode
        self.created_at = created_at
        self.staff_name = staff_name

    def to_dict(self):
        return {
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
            "staff_id": self.staff_id,
            "status": self.status,
            "street_number": self.street_number,
            "street_name": self.street_name,
            "suburb": self.suburb,
            "postcode": self.postcode,
            "created_at": self.created_at,
            "staff_name": self.staff_name,
        }
