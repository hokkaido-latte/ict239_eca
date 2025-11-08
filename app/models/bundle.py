from datetime import datetime
import json
#from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentListField, ReferenceField, StringField, BooleanField, DateTimeField, EmbeddedDocumentField, ObjectIdField, connect
from models.users import User
from models.package import Package
from app import db

class BundledPackages(db.EmbeddedDocument):
    package = db.ReferenceField(Package, required=True)
    utilised = db.BooleanField(default=False)

class Bundle(db.Document):

    meta = {'collection': 'bundles'}
    purchased_date = db.DateTimeField(required=True)
    customer = db.ReferenceField(User)
    bundledpackages = db.EmbeddedDocumentListField(BundledPackages)

    @staticmethod
    def createBundle(customer, package_list, purchase_date=None):
        if purchase_date is None:
            purchase_date = datetime.utcnow()
        bundled_packages = [BundledPackages(package=pkg) for pkg in package_list]
        bundle = Bundle(purchased_date=purchase_date, customer=customer, bundledpackages=bundled_packages).save()
        return bundle

    def to_json(self):
        return {
            "_id": str(self.id),
            "purchased_date": self.purchased_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "customer": str(self.customer.id) if self.customer else None,
            "bundledPackages": [
                {
                    "package": str(bp.package.id) if bp.package else None,
                    "utilised": bp.utilised
                }
                for bp in self.bundledpackages
            ]
        }

    @staticmethod
    def show_all_bundles():
        bundles = Bundle.objects()
        json_bundles = [bundle.to_json() for bundle in bundles]
        print(json.dumps(json_bundles, indent=4))
        return json_bundles
