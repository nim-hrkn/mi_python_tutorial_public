# -----------------------
# reverse diffusion
#
# x_T -> ... -> x_0
# -----------------------
@torch.no_grad()
def sample(model, n=10000):
    model.eval()

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

        eps_pred = model(
            x,
            k_batch,
        )

        mean = (
            1.0
            / torch.sqrt(alpha_k)
            * (x - beta_k / torch.sqrt(1.0 - alpha_bar_k) * eps_pred)
        )

        if k > 0:
            z = torch.randn_like(x)

            posterior_variance_k = posterior_variance[k]

            x = mean + torch.sqrt(posterior_variance_k) * z
        else:
            x = mean

    return x.cpu().numpy().ravel()
