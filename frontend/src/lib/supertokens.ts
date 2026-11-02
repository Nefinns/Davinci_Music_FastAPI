import SuperTokens from "supertokens-web-js"
import Session from "supertokens-web-js/recipe/session"

export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
SuperTokens.init({
  appInfo: { appName: "DaVinciMusic", apiDomain: API_URL, apiBasePath: "/auth" },
  recipeList: [Session.init({ tokenTransferMethod: "cookie" })],
})
export { Session }
