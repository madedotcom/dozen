import dozen
from expects import expect, equal, be_false, be_a, be_true, raise_error


class simple_template(dozen.Template):
    size: int
    my_bool: bool
    some_str: str
    bigness: float


class nested_template(dozen.Template):
    force: bool
    stuff: simple_template


class When_building_scalars_from_the_environment:
    def because_we_load_the_template(self):
        self.cfg = simple_template.build(
            env={
                "SIZE": "10",
                "MY_BOOL": "false",
                "SOME_STR": "sausage",
                "BIGNESS": "0.2",
            }
        )

    def it_should_have_the_correct_values(self):
        expect(self.cfg.size).to(equal(10))
        expect(self.cfg.my_bool).to(be_false)
        expect(self.cfg.some_str).to(equal("sausage"))
        expect(self.cfg.bigness).to(equal(0.2))


class When_there_is_an_error_parsing_some_value:
    def because_we_load_the_template(self):
        try:
            simple_template.build(
                env={
                    "SIZE": "sausage",
                    "MY_BOOL": "false",
                    "SOME_STR": "sausage",
                    "BIGNESS": "0.2",
                }
            )
        except Exception as e:
            self.exn = e

    def it_should_raise_value_error(self):
        expect(self.exn).to(be_a(ValueError))

    def it_should_have_a_useful_message(self):
        expect(str(self.exn)).to(
            equal(
                "Error parsing 'size' property of 'simple_template':\n"
                "invalid literal for int() with base 10: 'sausage'"
            )
        )


class When_building_with_a_prefix:
    def because_we_load_the_template(self):
        self.cfg = simple_template.build(
            env={
                "PREFIX_SIZE": "10",
                "PREFIX_MY_BOOL": "false",
                "PREFIX_SOME_STR": "sausage",
                "PREFIX_BIGNESS": "0.2",
            },
            prefix="PREFIX",
        )

    def it_should_have_the_correct_values(self):
        expect(self.cfg.size).to(equal(10))
        expect(self.cfg.my_bool).to(be_false)
        expect(self.cfg.some_str).to(equal("sausage"))
        expect(self.cfg.bigness).to(equal(0.2))


class When_building_nested_configuration_objects:
    def given_an_environment(self):
        self.env = {
            "FORCE": "1",
            "STUFF_SIZE": "7",
            "STUFF_MY_BOOL": "0",
            "STUFF_SOME_STR": "carbonara",
            "STUFF_BIGNESS": "7.8",
        }

    def because_we_load_the_template(self):
        self.cfg = nested_template.build(env=self.env)

    def it_should_have_the_correct_values(self):
        expect(self.cfg.force).to(be_true)
        expect(self.cfg.stuff.size).to(equal(7))
        expect(self.cfg.stuff.my_bool).to(be_false)
        expect(self.cfg.stuff.some_str).to(equal("carbonara"))
        expect(self.cfg.stuff.bigness).to(equal(7.8))


class When_keys_are_missing:

    ALL_VARS = {"SIZE": "7", "MY_BOOL": "0", "SOME_STR": "carbonara"}

    @classmethod
    def examples(cls):
        return cls.ALL_VARS.keys()

    def given_an_environment(self, k):
        self.env = self.ALL_VARS.copy()
        del self.env[k]

    def it_should_raise_key_error(self):
        expect(lambda: simple_template.build(env=self.env)).to(raise_error(KeyError))


class template_with_default(dozen.Template):
    size: int = 5
    my_bool: bool = True
    some_str: str = "foo"
    bigness: float = 0.1


class When_a_field_has_a_default_value:

    def because_we_build_the_config(self):
        self.cfg = template_with_default.build(env={'SIZE': 10})

    def it_should_apply_the_defaults(self):
        expect(self.cfg.my_bool).to(be_true)
        expect(self.cfg.some_str).to(equal("foo"))
        expect(self.cfg.bigness).to(equal(0.1))

    def it_should_override_default_with_env(self):
        expect(self.cfg.size).to(equal(10))
