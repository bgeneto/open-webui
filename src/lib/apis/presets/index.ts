import { WEBUI_API_BASE_URL } from '$lib/constants';

export const savePreset = async (token: string, preset: object) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/presets/save`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        },
        body: JSON.stringify(preset)
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err;
            console.log(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getPresets = async (token: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/presets/`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err;
            console.log(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getPresetByName = async (token: string, presetName: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/presets/${presetName}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err;
            console.log(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const deletePresetByName = async (token: string, presetName: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/presets/${presetName}`, {
        method: 'DELETE',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err;
            console.log(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};
