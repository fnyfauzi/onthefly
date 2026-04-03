export let toast: { value: string | null } = $state({ value: null });

/*
const _key: string = "momi2-user-toast";
const ttl: number = 60000;

export const setToast = (value: string | null) => {
  const now = new Date();
  const item = {
    value: value,
    expiry: now.getTime() + ttl,
  };
  localStorage.setItem(_key, JSON.stringify(item));
};

export const getToast = (): string | null => {
  const itemStr = localStorage.getItem(_key);
  if (!itemStr) return null;
  const item = JSON.parse(itemStr);
  const now = new Date();
  if (now.getTime() > item.expiry) {
    localStorage.removeItem(_key);
    return null;
  }
  return item.value;
};
*/

/*
class CreateToast {
  _value: string | null = $state(null);
  constructor(newValue: string | null) {
    this._value = newValue;
  }
  get value(): string | null {
    this._value = localStorage.getItem(this._key);
    return this._value;
  }
  set value(newValue: string | null) {
    this._value = newValue;
  }
}
export let toast = new CreateToast(null);
*/

/*
class CreateToast {
  _key: string = "momi2-user-state";

  constructor() {
    if (localStorage.getItem(this._key)) {
      localStorage.removeItem(this._key);
    }
  }

  get value(): string | null {
    return localStorage.getItem(this._key);
  }

  set value(newValue: string | null) {
    if (newValue === null) {
      if (localStorage.getItem(this._key)) {
        localStorage.removeItem(this._key);
      }
    } else {
      localStorage.setItem(this._key, newValue);
    }
  }
}

export let toast = new CreateToast();
*/
