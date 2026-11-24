# -----------------------
# reverse diffusion
#
# x_T -> ... -> x_0
# -----------------------
@torch.no_grad()
def sample(model, n=10000):
    model.eval()

    # -------------------
    # start from noise
    #
    # x_T ~ N(0, I)
    # -------------------
    x = torch.randn(
        n,
        1,
        device=device,
    )

    for k in reversed(range(T)):
        k_batch = torch.full(
            (n,),
            k,
            device=device,
            dtype=torch.long,
        )

        beta_k = betas[k]
        alpha_k = alphas[k]
        alpha_bar_k = alpha_bars[k]

        # -------------------
        # predict noise
        #
        # eps_theta(x_k, k)
        # -------------------
        eps_pred = model(
            x,
            k_batch,
        )

        # -------------------
        # DDPM reverse mean
        #
        # mu_theta(x_k, k)
        # =
        # 1 / sqrt(alpha_k)
        # [
        #   x_k
        #   -
        #   beta_k
        #   / sqrt(1-alpha_bar_k)
        #   * eps_theta(x_k,k)
        # ]
        # -------------------
        mean = (
            1.0
            / torch.sqrt(alpha_k)
            * (x - beta_k / torch.sqrt(1.0 - alpha_bar_k) * eps_pred)
        )

        # -------------------
        # sample x_{k-1}
        #
        # x_{k-1}
        # =
        # mean
        # +
        # sqrt(beta_tilde_k) z
        # -------------------
        if k > 0:
            z = torch.randn_like(x)

            posterior_variance_k = posterior_variance[k]

            x = mean + torch.sqrt(posterior_variance_k) * z
        else:
            # 最後のステップではnoiseを加えない
            x = mean

    return x.cpu().numpy().ravel()
