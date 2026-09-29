"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { useToast } from "@/components/common/Toast";
import { Sparkles, Lock, User as UserIcon } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const { login } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setErrorMessage("Please enter both username and password.");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    try {
      await login({ username, password });
      addToast({
        type: "success",
        title: "Signed In",
        description: `Welcome back, ${username}!`,
      });
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Invalid credentials. Please verify your username and password.";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Logo */}
        <div className="text-center space-y-2">
          <Link href="/dashboard" className="inline-flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-accent shadow-sm">
              <Sparkles className="w-5 h-5 fill-accent" />
            </div>
            <div className="text-left">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-base tracking-tight text-primary">MARKETMIND</span>
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-accent-light text-accent-dark border border-accent/30">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-content-muted font-medium">Financial Intelligence System</p>
            </div>
          </Link>
        </div>

        {/* Login Form */}
        <Card className="shadow-modal">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-lg">Sign In to MarketMind</CardTitle>
            <CardDescription>Enter your institutional credentials to continue</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4 pt-2">
              <Input
                label="Username or Email"
                placeholder="analyst@marketmind.ai"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                leftIcon={<UserIcon className="w-4 h-4" />}
                required
              />

              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                required
              />

              {errorMessage && (
                <div className="p-3 rounded-lg bg-financial-loss-bg text-financial-loss text-xs font-medium">
                  {errorMessage}
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full"
                isLoading={isLoading}
              >
                Sign In
              </Button>

              <div className="pt-2 text-center">
                <p className="text-xs text-content-muted">
                  Don&apos;t have an account?{" "}
                  <Link href="/register" className="text-primary font-bold hover:underline">
                    Create Account
                  </Link>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
