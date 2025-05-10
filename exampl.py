from app import db,create_app
from app.models import Branch,Permissions,Permission,User
# seed.py

from app import create_app, db
from app.models import Branch, User, Permissions, user_permissions

app = create_app()

with app.app_context():
    db.create_all()

    # ✳️ إضافة فروع
    branches = [ Branch(name="فرع صنعاء", location="صنعاء - الزريقي"),
                 Branch(name="فرع عدن", location="عدن - المنصورة"),
                 Branch(name="فرع ذمار", location="ذمار"),
                 Branch(name="فرع الحديدة", location="الحديدة")
                ]
    db.session.add_all(branches)
    db.session.commit()
    print("✅ تم تعبئة قاعدة الفروع بنجاح.")

    permission_choices = [
        Permissions.MANAGE_PRODUCTS,
        Permissions.MANAGE_USERS,
        Permissions.MANAGE_OFFERS,
        Permissions.VIEW_ALL_ORDERS,
        Permissions.VIEW_BRANCH_ORDERS,
        Permissions.VIEW_ALL_REPORTS,
        Permissions.VIEW_BRANCH_REPORTS,
        Permissions.VIEW_ALL_BRANCHES,
    ]

    # إضافة الصلاحيات إلى قاعدة البيانات (إذا لم تكن موجودة)
    for perm_name in permission_choices:
        if not Permission.query.filter_by(name=perm_name).first():
            p = Permission(name=perm_name, description=perm_name.replace('_', ' ').title())
            db.session.add(p)

    db.session.commit()
    print("✅ تم تعبئة قاعدة الصلاحيات بنجاح.")


      # ✳️ إنشاء المدير بصلاحيات كاملة
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", branch_id=1)
        admin.set_password("admin123")

        all_permissions = Permission.query.all()
        admin.permissions.extend(all_permissions)

        db.session.add(admin)
        db.session.commit()

    print("✅ تم تعبئة الادمن  بنجاح.")


