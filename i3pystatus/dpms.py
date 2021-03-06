from i3pystatus import IntervalModule
from i3pystatus.core.command import run_through_shell


class DPMS(IntervalModule):
    """
    Shows and toggles status of DPMS which prevents screen from blanking.

    .. rubric:: Available formatters

    * `{status}` — the current status of DPMS

    @author Georg Sieber <g.sieber AT gmail.com>
    """

    interval = 5

    settings = (
        "format",
        "color",
        "color_disabled",
    )

    color_disabled = "#AAAAAA"
    color = "#FFFFFF"
    format = "DPMS: {status}"

    on_leftclick = "toggle_dpms"

    status = False

    def run(self):

        self.status = run_through_shell("xset -q | grep -q 'DPMS is Enabled'", True).rc == 0

        self.output = {
            "full_text": self.format.format(status='on' if self.status else 'off'),
            "color": self.color if self.status else self.color_disabled
        }

    def toggle_dpms(self):
        if self.status:
            run_through_shell("xset -dpms s off", True)
        else:
            run_through_shell("xset +dpms s on", True)
