import { api } from '$lib/utils/api';

export const savePreset = async (preset) => {
  const response = await api.post('/presets/save', preset);
  return response.data;
};

export const loadPresets = async () => {
  const response = await api.get('/presets');
  return response.data;
};

export const deletePreset = async (presetName) => {
  const response = await api.delete(`/presets/${presetName}`);
  return response.data;
};
