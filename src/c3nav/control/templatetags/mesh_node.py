from django import template
from django.urls import reverse
from django.utils.html import format_html

from c3nav.mesh.models import MeshNode

register = template.Library()


@register.simple_tag(takes_context=True)
def mesh_node(context, node: str | MeshNode):
    if isinstance(node, str):
        bssid = node
        name = context.get("node_names", {}).get(node, None)
    else:
        bssid = node.address
        name = node.name
    if name:
        return format_html(
            '<a href="{url}">{bssid}</a> ({name})',
            url=reverse('control.mesh.node.detail', kwargs={"pk": bssid}), bssid=bssid, name=name
        )
    else:
        return format_html(
            '<a href="{url}">{bssid}</a>',
            url=reverse('control.mesh.node.detail', kwargs={"pk": bssid}), bssid=bssid
        )


@register.filter()
def m_to_cm(value):
    return "%.2fm" % (int(value)/100)