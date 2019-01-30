import dozen
from expects import expect, equal, be_a


class simple_template(dozen.Template):
    db: dozen.service()


class When_building_services_from_environment:
    def because_we_load_the_template(self):
        self.cfg = simple_template.build(env={
            "DB_HOST": "db.local",
            "DB_PORT": "5432"
        })

    def it_should_build_the_service(self):
        expect(self.cfg.db.host).to(equal("db.local"))
        expect(self.cfg.db.port).to(equal(5432))


class template_with_defaults(dozen.Template):
    db: dozen.service(default_port=5432)
    web: dozen.service(default_host="web.local")
    api: dozen.service(default_host="api.local", default_port=1234)
    admin: dozen.service(default_host="admin.local", default_port=2345)


class When_providing_defaults:
    def because_we_build_the_template(self):
        self.cfg = template_with_defaults.build(
            env={
                "DB_HOST": "db.server",
                "WEB_PORT": "2345",
                "API_HOST": "api.server",
                "ADMIN_PORT": "3456",
            })

    def it_should_provide_a_default_port(self):
        expect(self.cfg.db.port).to(equal(5432))
        expect(self.cfg.db.host).to(equal("db.server"))

    def it_should_provide_a_default_host(self):
        expect(self.cfg.web.host).to(equal("web.local"))
        expect(self.cfg.web.port).to(equal(2345))

    def it_should_prefer_specified_host(self):
        expect(self.cfg.api.host).to(equal("api.server"))

    def it_should_prefer_specified_port(self):
        expect(self.cfg.admin.port).to(equal(3456))


class When_a_port_is_non_numeric:
    def because_we_load_the_template(self):
        try:
            self.cfg = simple_template.build(env={
                "DB_HOST": "db.local",
                "DB_PORT": "not a number"
            })
        except Exception as e:
            self.exn = e

    def it_should_raise_value_error(self):
        expect(self.exn).to(be_a(ValueError))
