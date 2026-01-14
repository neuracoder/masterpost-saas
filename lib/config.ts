interface Environment {
  name: string;
  apiUrl: string;
  frontendUrl: string;
}

interface Config {
  environments: {
    development: Environment;
    production: Environment;
  };
  current: Environment;
}

const config: Config = {
  environments: {
    development: {
      name: 'development',
      apiUrl: 'http://localhost:8002',
      frontendUrl: 'http://localhost:3000'
    },
    production: {
      name: 'production',
      apiUrl: 'https://masterpost-io.onrender.com',
      frontendUrl: 'https://masterpost-io.netlify.app'
    }
  },
  get current() {
    // En el navegador
    if (typeof window !== 'undefined') {
      return process.env.NEXT_PUBLIC_NODE_ENV === 'production' 
        ? this.environments.production 
        : this.environments.development;
    }
    // En el servidor
    return process.env.NODE_ENV === 'production'
      ? this.environments.production
      : this.environments.development;
  }
};

export const getCurrentEnvironment = () => config.current;

export const getApiUrl = () => {
  // Primero intentamos obtener la URL de la variable de entorno
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl) {
    return envUrl;
  }

  // Si no hay variable de entorno, usamos la configuración según el entorno
  return config.current.apiUrl;
};

export const getFrontendUrl = () => {
  // Primero intentamos obtener la URL de la variable de entorno
  const envUrl = process.env.NEXT_PUBLIC_FRONTEND_URL;
  if (envUrl) {
    return envUrl;
  }

  // Si no hay variable de entorno, usamos la configuración según el entorno
  return config.current.frontendUrl;
};

export default config;