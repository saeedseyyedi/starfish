from typing import Mapping, MutableMapping, Union

import numpy as np
import xarray as xr

from starfish.types import Axes, Coordinates


def convert_to_selector(
        indexers: Mapping[Axes, Union[int, slice, tuple]]) -> Mapping[str, Union[int, slice]]:
    """Converts a mapping of Axis to int, slice, or tuple to a mapping of str to int or slice.  The
    latter format is required for standard xarray indexing methods.

    Parameters
    ----------
    indexers : Mapping[Axes, Union[int, slice, tuple]]
            A dictionary of dim:index where index is the value or range to index the dimension

    """
    return_dict: MutableMapping[str, Union[int, slice]] = {
        ind.value: slice(None, None) for ind in Axes}
    for key, value in indexers.items():
        if isinstance(value, tuple):
            return_dict[key.value] = slice(value[0], value[1])
        else:
            return_dict[key.value] = value
    return return_dict


def convert_coords_to_indices(array: xr.DataArray, indexers
                              ) -> Mapping[Axes, Union[int, tuple]]:
    if Coordinates.X in indexers:
        if Axes.X in indexers:
            raise KeyError("Cannot index by both pixel and physical value of X")
        idx_x = find_nearest(array[Coordinates.X.value],
                             indexers[Coordinates.X])
        del indexers[Coordinates.X]
        indexers[Axes.X] = idx_x
    if Coordinates.Y in indexers:
        if Axes.Y in indexers:
            raise KeyError("Cannot index by both pixel and physical value of Y")
        idx_y = find_nearest(array[Coordinates.Y.value],
                             indexers[Coordinates.Y])
        del indexers[Coordinates.Y]
        indexers[Axes.Y] = idx_y
    if Coordinates.Z in indexers:
        if Axes.ZPLANE in indexers:
            raise KeyError("Cannot index by both pixel and physical value of Z")
        idx_z = find_nearest(array[Coordinates.Z.value],
                             indexers[Coordinates.Z])
        del indexers[Coordinates.Z]
        indexers[Axes.ZPLANE] = idx_z
    return indexers


def index_keep_dimensions(data: xr.DataArray,
                          indexers: Mapping[str, Union[int, slice]],
                          ) -> xr.DataArray:
    """Takes an xarray and key to index it. Indexes then adds back in lost dimensions"""
    # store original dims
    original_dims = data.dims
    # index
    data = data.sel(indexers)
    # find missing dims
    missing_dims = set(original_dims) - set(data.dims)
    # Add back in missing dims
    data = data.expand_dims(tuple(missing_dims))
    # Reorder to correct format
    return data.transpose(*original_dims)


def find_nearest(array: xr.DataArray, value: Union[float, tuple]
                 ) -> Union[int, tuple]:
    """
    Given an xarray and value or tuple range return the indices of the closest corresponding
    value/values in the array.

    Parameters
    ----------
    array: xr.DataArray
        he array to do lookups in.

    value:  Union[float, tuple]
        The value or values to lookup.

    Returns
    -------
    Union[int, tuple]:
        The index or indicies of the entries closest to the given values in the array.
    """
    array = np.asarray(array)
    if isinstance(value, tuple):
        idx1 = (np.abs(array - value[0])).argmin()
        idx2 = (np.abs(array - value[1])).argmin()
        return idx1, idx2
    idx = (np.abs(array - value)).argmin()
    return idx
