from __future__ import annotations

import pygame

from settings import COLORS, TYPE_COLORS


INK = COLORS["ink"]
WHITE = COLORS["white"]


def text(
    surface,
    font,
    value,
    pos,
    color=INK,
    anchor="topleft",
    shadow=True,
):
    """
    Testo nitido pensato per pixel art.

    Il testo scuro sui pannelli chiari non usa
    un'ombra luminosa, evitando l'effetto
    doppio/sfocato durante lo scaling.
    """

    value=str(value)

    img=font.render(
        value,
        False,
        color,
    )

    rect=img.get_rect()

    setattr(
        rect,
        anchor,
        pos,
    )

    if shadow:

        luminance=(
            color[0]
            +
            color[1]
            +
            color[2]
        )

        if luminance>430:

            shadow_img=font.render(
                value,
                False,
                COLORS["shadow"],
            )

            shadow_rect=rect.copy()

            shadow_rect.x+=1
            shadow_rect.y+=1

            surface.blit(
                shadow_img,
                shadow_rect,
            )

    surface.blit(
        img,
        rect,
    )

    return rect


def panel(
    surface,
    rect,
    fill=None,
    border=None,
    radius=3,
):

    rect=pygame.Rect(
        rect
    )

    fill=(
        fill
        or
        COLORS["panel"]
    )

    border=(
        border
        or
        INK
    )

    pygame.draw.rect(
        surface,
        (
            14,
            23,
            29,
        ),
        rect.move(
            2,
            2,
        ),
        border_radius=radius,
    )

    pygame.draw.rect(
        surface,
        fill,
        rect,
        border_radius=radius,
    )

    pygame.draw.rect(
        surface,
        border,
        rect,
        2,
        border_radius=radius,
    )

    pygame.draw.line(
        surface,
        (
            255,
            250,
            230,
        ),
        (
            rect.x+3,
            rect.y+3,
        ),
        (
            rect.right-4,
            rect.y+3,
        ),
    )

    return rect


def hp_bar(
    surface,
    rect,
    ratio,
):

    rect=pygame.Rect(
        rect
    )

    ratio=max(
        0,
        min(
            1,
            ratio,
        ),
    )

    pygame.draw.rect(
        surface,
        (
            56,
            70,
            65,
        ),
        rect,
    )

    if ratio>0:

        if ratio>.5:

            color=COLORS[
                "green"
            ]

        elif ratio>.25:

            color=(
                226,
                183,
                74,
            )

        else:

            color=COLORS[
                "red"
            ]

        fill=rect.copy()

        fill.width=max(
            1,
            int(
                rect.width
                *
                ratio
            ),
        )

        pygame.draw.rect(
            surface,
            color,
            fill,
        )

    pygame.draw.rect(
        surface,
        (
            38,
            50,
            50,
        ),
        rect,
        1,
    )


def type_badge(
    surface,
    font,
    value,
    rect,
):

    rect=pygame.Rect(
        rect
    )

    color=TYPE_COLORS.get(
        value,
        (
            160,
            160,
            160,
        ),
    )

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=3,
    )

    pygame.draw.rect(
        surface,
        INK,
        rect,
        1,
        border_radius=3,
    )

    text(
        surface,
        font,
        value,
        rect.center,
        WHITE,
        "center",
        False,
    )


def button(
    surface,
    font,
    rect,
    label,
    selected=False,
    enabled=True,
    accent=False,
):
    """
    Pulsante ad alto contrasto.

    Ritorna il pygame.Rect per permettere
    l'uso anche come area cliccabile.
    """

    rect=pygame.Rect(
        rect
    )

    if not enabled:

        fill=(
            160,
            163,
            151,
        )

        label_color=(
            86,
            91,
            88,
        )

    elif selected:

        fill=(
            205,
            231,
            163,
        )

        label_color=INK

    elif accent:

        fill=(
            240,
            211,
            133,
        )

        label_color=INK

    else:

        fill=(
            244,
            236,
            211,
        )

        label_color=INK

    # Ombra pulsante

    pygame.draw.rect(
        surface,
        (
            18,
            29,
            34,
        ),
        rect.move(
            1,
            2,
        ),
        border_radius=3,
    )

    # Fondo

    pygame.draw.rect(
        surface,
        fill,
        rect,
        border_radius=3,
    )

    # Bordo

    pygame.draw.rect(
        surface,
        INK,
        rect,
        2
        if selected
        else 1,
        border_radius=3,
    )

    if selected:

        pygame.draw.polygon(
            surface,
            INK,
            [
                (
                    rect.x+4,
                    rect.centery-3,
                ),
                (
                    rect.x+9,
                    rect.centery,
                ),
                (
                    rect.x+4,
                    rect.centery+3,
                ),
            ],
        )

        text(
            surface,
            font,
            label,
            (
                rect.x+12,
                rect.centery,
            ),
            label_color,
            "midleft",
            False,
        )

    else:

        text(
            surface,
            font,
            label,
            rect.center,
            label_color,
            "center",
            False,
        )

    return rect


def wrap_text(
    font,
    message,
    max_width,
    max_lines=3,
):

    words=str(
        message
    ).split()

    lines=[]

    current=""

    for word in words:

        candidate=(
            current
            +
            " "
            +
            word
        ).strip()

        if (
            current
            and
            font.size(
                candidate
            )[0]
            >
            max_width
        ):

            lines.append(
                current
            )

            current=word

            if len(lines)>=max_lines:
                break

        else:

            current=candidate

    if (
        current
        and
        len(lines)<max_lines
    ):

        lines.append(
            current
        )

    return lines[
        :max_lines
    ]


def dialogue(
    surface,
    assets,
    message,
    hint="",
    rect=(
        5,
        123,
        130,
        52,
    ),
):
    """
    Finestra di dialogo leggibile.

    Il rect può essere cambiato
    dalle schermate battaglia/mondo.
    """

    r=panel(
        surface,
        rect,
        COLORS["panel"],
    )

    lines=wrap_text(
        assets.font,
        message,
        max(
            20,
            r.width-14,
        ),
        3,
    )

    line_height=max(
        10,
        assets.font.get_linesize()-2,
    )

    start_y=r.y+7

    for index,line in enumerate(
        lines
    ):

        text(
            surface,
            assets.font,
            line,
            (
                r.x+7,
                start_y
                +
                index
                *
                line_height,
            ),
            INK,
            shadow=False,
        )

    if hint:

        text(
            surface,
            assets.font_tiny,
            hint,
            (
                r.right-6,
                r.bottom-4,
            ),
            (
                68,
                80,
                76,
            ),
            "bottomright",
            False,
        )

    return r