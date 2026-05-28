class PaymentMethod:
    def __init__(
        self,
        payment_method_id,
        user_id,
        method_type,
        nickname,
        created_at,
        updated_at=None,
        cardholder_name=None,
        card_brand=None,
        card_last_four=None,
        expiry_date=None,
        account_name=None,
        bsb_last_three=None,
        account_last_four=None,
        paypal_email_masked=None,
    ):
        self.payment_method_id = payment_method_id
        self.user_id = user_id
        self.method_type = method_type
        self.nickname = nickname
        self.created_at = created_at
        self.updated_at = updated_at
        self.cardholder_name = cardholder_name
        self.card_brand = card_brand
        self.card_last_four = card_last_four
        self.expiry_date = expiry_date
        self.account_name = account_name
        self.bsb_last_three = bsb_last_three
        self.account_last_four = account_last_four
        self.paypal_email_masked = paypal_email_masked

    def to_dict(self):
        return {
            "id": str(self.payment_method_id).zfill(3),
            "payment_method_id": self.payment_method_id,
            "user_id": self.user_id,
            "type": self.method_type,
            "nickname": self.nickname,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "cardholderName": self.cardholder_name,
            "cardBrand": self.card_brand,
            "cardLastFour": self.card_last_four,
            "expiryDate": self.expiry_date,
            "accountName": self.account_name,
            "bsbLastThree": self.bsb_last_three,
            "accountLastFour": self.account_last_four,
            "paypalEmail": self.paypal_email_masked,
        }
