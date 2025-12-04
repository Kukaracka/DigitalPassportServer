export const clearAuthCookies = () => {
  const cookies = [
    'my_access_token',
    'access_token',
    'token',
    'session'
  ];
  
  const domains = ['', '.localhost', window.location.hostname];
  
  cookies.forEach(cookieName => {
    domains.forEach(domain => {
      document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${domain};`;
    });
  });
};

export const setManualLogoutFlag = () => {
  localStorage.setItem('manualLogout', 'true');
  sessionStorage.setItem('manualLogout', 'true');
};

export const clearManualLogoutFlag = () => {
  localStorage.setItem('manualLogout', 'false');
  sessionStorage.setItem('manualLogout', 'false');
};

export const isManualLogout = () => {
  return localStorage.getItem('manualLogout') === 'true' || 
         sessionStorage.getItem('manualLogout') === 'true';
};