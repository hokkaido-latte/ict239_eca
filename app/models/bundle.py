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
    customer = db.ReferenceField(User, required=False)
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

    @staticmethod
    def get_bundles_by_customer(customer):
        return Bundle.objects(customer=customer)

    @staticmethod
    def get_all_bundles():
        return Bundle.objects

    #write a method to get bundles by purchase date
    @staticmethod
    def get_bundles_by_purchase_date(purchase_date):
        start = datetime.combine(purchase_date, datetime.min.time())
        end = datetime.combine(purchase_date, datetime.max.time())
        return Bundle.objects(purchased_date__gte=start, purchased_date__lte=end)

    #write a method to delete all bundles
    @staticmethod
    def delete_all_bundles():
        Bundle.objects.delete()

    def checkInBundle(bundle_id, package_id, customer):
        #check_in_dt = datetime.strptime(check_in_date_str, "%Y-%m-%d")

        bundle = Bundle.objects(id=bundle_id, customer=customer).first()
        if not bundle:
            return False

        for bp in bundle.bundledpackages:
            if str(bp.package.id) == str(package_id):
                bp.utilised = True
                #bp.check_in_date = check_in_dt
                bundle.save()
                return True

        return False

