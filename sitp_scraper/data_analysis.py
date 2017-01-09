from math import sqrt

from sitp_scraper.models import Route


def distance(x1, y1, x2, y2):
    return sqrt(
        (x1 - x2)**2
        + (y1 - y2)**2
    )


def avg(values):
    return sum(values) / len(values)


def stddev(values):
    u = avg(values)
    return u, sqrt(
        sum((v - u)**2 for v in values) / len(values)
    )


def distances_next_station(route_stations):
    dists_ns = [
        distance(
            rs.bus_station.latitude,
            rs.bus_station.longitude,
            nrs.bus_station.latitude,
            nrs.bus_station.longitude,
        ) / abs(rs.position - nrs.position)
        for rs, nrs in zip(route_stations[:-1], route_stations[1:])
    ]
    dists_ns.append(dists_ns[-1])

    return dists_ns


def outliers(values):
    u, sd = stddev(values)

    outliers = [
        i for i, d in enumerate(values)
        if d >= u + (4 * sd)
    ]

    return outliers


def _bus_route_outliers(route, direction, known_outlier_rs_ids):
    route_stations = [
        rs
        for rs in route.route_stations.select_related("bus_station")\
            .filter(
                direction=direction,
                bus_station__latitude__isnull=False,
                bus_station__longitude__isnull=False,
            ).exclude(id__in=known_outlier_rs_ids).order_by("position")
    ]

    if not route_stations:
        return []

    dists_ns = distances_next_station(route_stations)
    dists_ps = distances_next_station(list(reversed(route_stations)))

    outliers_ns = set(outliers(dists_ns))
    outliers_ps = set(len(route_stations) - 1 - i for i in outliers(dists_ps))

    return [
        route_stations[i]
        for i in outliers_ns & outliers_ps
    ]


def bus_route_outliers(route, direction):
    outliers = set()
    while True:
        n_outs = _bus_route_outliers(route, direction, [o.id for o in outliers])

        if not n_outs:
            break

        outliers.update(n_outs)
    return outliers


def _calc_global_stats():
    distances = []
    for direction in (1, 2):
        for route in Route.objects.all():
            route_stations = [
                rs
                for rs in route.route_stations.select_related("bus_station")\
                    .filter(
                        direction=direction,
                        bus_station__latitude__isnull=False,
                        bus_station__longitude__isnull=False,
                    ).order_by("position")
            ]

            if not route_stations:
                continue

            distances.extend(distances_next_station(route_stations))
    return stddev(distances)
