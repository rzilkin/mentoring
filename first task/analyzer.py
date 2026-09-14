from math import floor, ceil


class Analyzer:
    def __init__(self, columns: dict[str, list[float]]) -> None:
        self.columns = columns
        self._sorted_columns = {k: sorted(v) for k, v in self.columns.items()}
        self.length = len(next(iter(columns.values())))
        self.result = {k: [] for k in self.columns}
        self.result['metrics'] = []

    def _calc_avg(self) -> dict[str, float]:
        return {k: sum(v) / self.length for k, v in self.columns.items()}

    def avg(self) -> dict[str, float]:
        avg = self._calc_avg()
        self.result['metrics'].append('avg')
        for k, v in avg.items():
            self.result[k].append(v)

        return avg

    def _calc_std(self) -> dict[str, float]:
        avg = self._calc_avg()
        std = {}
        for k, val in self.columns.items():
            d = sum((v - avg[k]) ** 2 for v in val) / self.length
            std[k] = d ** 0.5
        return std

    def std(self) -> dict[str, float]:
        std = self._calc_std()
        self.result['metrics'].append('std')
        for k, v in std.items():
            self.result[k].append(v)

        return std

    def _calc_median(self) -> dict[str, float]:
        median = {}
        is_even = self.length % 2 == 0
        mid = self.length // 2
        for k, buff in self._sorted_columns.items():
            median[k] = (
                buff[mid] if not is_even else (buff[mid] + buff[mid - 1]) / 2
            )
        return median

    def median(self) -> dict[str, float]:
        median = self._calc_median()
        self.result['metrics'].append('median')
        for k, v in median.items():
            self.result[k].append(v)
        return median

    def _calc_min(self) -> dict[str, float]:
        return {k: min(v) for k, v in self.columns.items()}

    def min_in_column(self) -> dict[str, float]:
        min_vals = self._calc_min()
        self.result['metrics'].append('min')
        for k, v in min_vals.items():
            self.result[k].append(v)
        return min_vals

    def _calc_max(self) -> dict[str, float]:
        return {k: max(v) for k, v in self.columns.items()}

    def max_in_column(self) -> dict[str, float]:
        max_vals = self._calc_max()
        self.result['metrics'].append('max')
        for k, v in max_vals.items():
            self.result[k].append(v)
        return max_vals

    def _calc_quantile(self, p: float) -> dict[str, float]:
        if not 0.0 <= p <= 1.0:
            raise ValueError('Параметр p должен лежать в диапазоне [0.0, 1.0]')

        quantiles = {}
        for k, buff in self._sorted_columns.items():
            idx = p * (self.length - 1)
            low = int(floor(idx))
            high = int(ceil(idx))
            fraction = idx - low

            quantiles[k] = buff[low] + fraction * (buff[high] - buff[low])
        return quantiles

    def quantile(self, p: float) -> dict[str, float]:
        q = self._calc_quantile(p)
        self.result['metrics'].append(f'quantile({p})')
        for k, v in q.items():
            self.result[k].append(v)
        return q

    def _calc_mode(self) -> dict[str, float | str]:
        modes = {}
        for k, v in self.columns.items():
            counts = {}
            for x in v:
                counts[x] = counts.get(x, 0) + 1

            max_count = max(counts.values())

            if max_count == 1:
                modes[k] = 'No mode'
                continue

            all_modes = [val for val, cnt in counts.items() if cnt == max_count]

            if len(all_modes) == 1:
                modes[k] = all_modes[0]
            else:
                modes[k] = '; '.join(map(str, all_modes))

        return modes

    def mode(self) -> dict[str, float | str]:
        modes = self._calc_mode()
        self.result['metrics'].append('mode')
        for k, v in modes.items():
            self.result[k].append(v)
        return modes

    def _calc_covariance(self, target: str) -> dict[str, float]:
        if target not in self.columns:
            raise KeyError(f"Столбец '{target}' отсутствует в данных")

        avg = self._calc_avg()
        target_vals = self.columns[target]
        target_mean = avg[target]

        cov_res = {}
        for k, v in self.columns.items():
            col_mean = avg[k]
            cov = (
                    sum((xi - col_mean) * (yi - target_mean) for xi, yi in zip(v, target_vals)) / self.length
            )
            cov_res[k] = cov
        return cov_res

    def covariance(self, target: str) -> dict[str, float]:
        cov_res = self._calc_covariance(target)
        self.result['metrics'].append(f'cov({target})')
        for k, v in cov_res.items():
            self.result[k].append(v)
        return cov_res

    def _calc_correlation(self, target: str) -> dict[str, float | None]:
        cov_res = self._calc_covariance(target)
        std = self._calc_std()
        target_std = std[target]

        corr_res = {}
        for k, cov in cov_res.items():
            col_std = std[k]
            if col_std == 0 or target_std == 0:
                corr_res[k] = None
            else:
                corr_res[k] = cov / (col_std * target_std)
        return corr_res

    def correlation(self, target: str) -> dict[str, float | None]:
        corr_res = self._calc_correlation(target)
        self.result['metrics'].append(f'corr({target})')
        for k, v in corr_res.items():
            self.result[k].append(v)
        return corr_res
