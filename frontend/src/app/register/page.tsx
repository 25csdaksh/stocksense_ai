"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { useToast } from "@/components/common/Toast";
import { Sparkles, Lock, Mail, User as UserIcon } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const { register } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !username || !password) {
      setErrorMessage("Please complete all required fields.");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    try {
      await register({
        email,
        username,
        password,
        full_name: fullName || undefined,
      });
      addToast({
        type: "success",
        title: "Account Created",
        description: "Your MarketMind AI workspace is ready.",
      });
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed. Username or email may already be in use.";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
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
              <p className="text-[10px] text-content-muted font-medium">Financial Intelligence Platform</p>
            </div>
          </Link>
        </div>

        {/* Register Card */}
        <Card className="shadow-modal">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-lg">Create Analyst Workspace</CardTitle>
            <CardDescription>Join institutional researchers and quantitative analysts</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3.5 pt-2">
              <Input
                label="Email Address"
                type="email"
                placeholder="analyst@firm.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail className="w-4 h-4" />}
                required
              />

              <Input
                label="Username"
                placeholder="daksh_quant"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                leftIcon={<UserIcon className="w-4 h-4" />}
                required
              />

              <Input
                label="Full Name (Optional)"
                placeholder="Daksh Patel"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                leftIcon={<UserIcon className="w-4 h-4" />}
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
                variant="gold"
                size="md"
                className="w-full mt-2"
                isLoading={isLoading}
              >
                Create Account
              </Button>

              <div className="pt-2 text-center">
                <p className="text-xs text-content-muted">
                  Already have an account?{" "}
                  <Link href="/login" className="text-primary font-bold hover:underline">
                    Sign In
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
