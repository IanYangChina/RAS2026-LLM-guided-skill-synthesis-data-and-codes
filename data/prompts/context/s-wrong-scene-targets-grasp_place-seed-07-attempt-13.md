## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3971 | 0.14 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5277 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3858 | 0.16 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5282 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4531 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5125095466604667, 0.039721380096957554, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5125095466604667, 0.039721380096957554, 0.03]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.397) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
phases:
- id: approach_pre_grasp
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_success
    when: during_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: continue
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 2.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_success, when=during_phase, predicate=pose_within_tolerance, on_failure=continue, threshold=0.02
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.397
- **task_score** (E): 0.142
- **fitness_score**: 0.158  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 0.00 | 1.00 | 0.1786 |
| descend_to_grasp | 1.00 | 1.00 | 0.0000 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 0.00 | 1.00 | 0.0009 |
| approach_goal | 0.33 | 1.00 | 0.1264 |
| descend_place | 0.00 | 1.00 | 0.0559 |
| release | 1.00 | 1.00 | 0.0263 |
| retract | 0.33 | 1.00 | 0.0824 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.403, 0.043, 0.157) | (0.511, 0.022, 0.030)→(0.466, 0.023, 0.016) | 0.271→0.299 | 1.00 / 5.000 | 212.244 | 1538.319 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.403, 0.043, 0.157)→(0.403, 0.043, 0.157) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 5.000 | 102.291 | 102.291 |
| grasp | grasp | 1.00 / step_budget | (0.403, 0.043, 0.157)→(0.403, 0.043, 0.157) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 9.333 | 91047.760 | 85.253 |
| lift | lift | 0.00 / step_budget | (0.499, 0.138, 0.211)→(0.500, 0.138, 0.212) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 9.000 | 324.543 | 491.862 |
| approach_goal | approach | 0.33 / step_budget | (0.500, 0.138, 0.212)→(0.498, 0.035, 0.169) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 9.667 | 91249.840 | 341.057 |
| descend_place | descend | 0.00 / step_budget | (0.498, 0.035, 0.169)→(0.509, 0.033, 0.218) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 9.333 | 162.337 | 267.320 |
| release | release | 1.00 / step_budget | (0.509, 0.033, 0.218)→(0.510, 0.032, 0.244) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 5.000 | 110.498 | 169.779 |
| retract | retract | 0.33 / step_budget | (0.510, 0.032, 0.244)→(0.490, 0.009, 0.186) | (0.466, 0.023, 0.016)→(0.466, 0.023, 0.016) | 0.299→0.299 | 1.00 / 5.333 | 32.704 | 136.856 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.197
- phase_score: 0.107
- phase_breakdown.approach_object_score: 0.136
- phase_breakdown.grasp_object_score: 0.052
- phase_breakdown.lift_object_score: 0.261
- phase_breakdown.place_at_goal_score: 0.011
- grasp_place_fitness: 0.188

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.188
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.197
- **Median Q (composite search score)**: -0.395
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 6.3
- **Final σ (mean)**: 0.403


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":165.0,"average_failure_rate":0.48961,"average_mean_iterations":101.4362,"average_solve_count":337.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.08983,"approach_pre_grasp.speed":0.02079,"descend_place.speed":0.03719,"descend_to_grasp.force_threshold":8.59815,"descend_to_grasp.speed":0.03156,"grasp.grasp_duration":1.09926,"lift.lift_height":0.08174,"lift.speed":0.02357,"release.release_duration":0.72831,"retract.speed":0.0775},"optimized_scores":{"best_composite_score":-0.36664,"best_fitness_score":0.18836,"best_task_score":0.1967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":883.0,"contact_point_centroid":[0.64216,0.02982,-0.00047],"force_p95":205.83598,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1598.74049,"mean_force":206.21916,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40524,0.03069,0.13189]},{"body_a":"link5","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.52248,0.0085,0.16556],"force_p95":561.79739,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":576.84112,"mean_force":441.74342,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48155,0.09959,0.17422]},{"body_a":"world","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.64328,0.04179,-6e-05],"force_p95":380.02145,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.7002,"mean_force":215.6265,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42257,0.04873,0.16164]},{"body_a":"link5","body_b":"hand","contact_count":18.0,"contact_point_centroid":[0.52287,0.00948,0.16559],"force_p95":330.93774,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.35897,"mean_force":279.84576,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48191,0.10038,0.17779]},{"body_a":"world","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.70399,0.07252,-8e-05],"force_p95":263.18843,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.09759,"mean_force":163.90946,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.472,0.06848,0.16324]},{"body_a":"link5","body_b":"hand","contact_count":410.0,"contact_point_centroid":[0.52859,-0.02939,0.19363],"force_p95":235.04838,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.0458,"mean_force":187.01817,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.49051,0.0615,0.21502]},{"body_a":"world","body_b":"link6","contact_count":35.0,"contact_point_centroid":[0.70032,0.08477,-0.00012],"force_p95":249.76692,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.8478,"mean_force":158.89363,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47312,0.08081,0.16757]},{"body_a":"link5","body_b":"hand","contact_count":146.0,"contact_point_centroid":[0.54633,-0.0256,0.28068],"force_p95":111.18114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.79858,"mean_force":48.10974,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.50884,0.0604,0.32368]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63512,0.0375,-0.00026],"force_p95":101.45221,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.45221,"mean_force":101.45221,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41488,0.04391,0.16087]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.636,0.03712,-0.00013],"force_p95":77.55029,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.56074,"mean_force":71.63952,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41527,0.04361,0.16044]},{"body_a":"grasp_target","body_b":"link7","contact_count":290.0,"contact_point_centroid":[0.50088,0.02433,0.03818],"force_p95":1.27099,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.04285,"mean_force":0.48576,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39838,0.0234,0.10649]},{"body_a":"grasp_target","body_b":"hand","contact_count":263.0,"contact_point_centroid":[0.49117,0.02287,0.05483],"force_p95":2.35764,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.14207,"mean_force":0.5042,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39812,0.02313,0.10429]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.47907,0.04159,-0.00273],"force_p95":0.32785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.19902,"mean_force":0.18221,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.41969,0.0298,0.14523]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46687,0.04204,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41488,0.04391,0.16087]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.46687,0.04204,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41527,0.04361,0.16044]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.46687,0.04204,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45314,0.0712,0.16591]}],"total_contact_groups":26},"final_pose_error":0.02918,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.46687,0.04204,0.01602],"final_tcp_position":[0.47461,0.04115,0.19414],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.12056,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":203.66591,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4773.0,"raw_peak_contact_force":1598.74049,"subtask_id":"approach_object","tcp_end":[0.41488,0.04391,0.16087],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1539,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":101.45221,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":101.45221,"subtask_id":"grasp_object","tcp_end":[0.41489,0.04386,0.16085],"tcp_start":[0.41488,0.04391,0.16087],"tcp_to_object_dist_end":0.15388,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":273004.12056,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3497.0,"raw_peak_contact_force":84.56074,"tcp_end":[0.41532,0.04357,0.16031],"tcp_start":[0.41532,0.04358,0.16031],"tcp_to_object_dist_end":0.15322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":400.78913,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2205.0,"raw_peak_contact_force":576.84112,"subtask_id":"lift_object","tcp_end":[0.48236,0.09979,0.17745],"tcp_start":[0.48216,0.0997,0.17634],"tcp_to_object_dist_end":0.17215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":453.58705,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":336.35897,"tcp_end":[0.47059,0.07154,0.16662],"tcp_start":[0.48236,0.09979,0.17745],"tcp_to_object_dist_end":0.1535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":168.3685,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5928.0,"raw_peak_contact_force":328.09759,"subtask_id":"place_at_goal","tcp_end":[0.50837,0.06021,0.31941],"tcp_start":[0.47059,0.07154,0.16662],"tcp_to_object_dist_end":0.30675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1173.0,"raw_peak_contact_force":134.79858,"tcp_end":[0.50948,0.0603,0.34916],"tcp_start":[0.50837,0.06021,0.31941],"tcp_to_object_dist_end":0.33635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46687,0.04204,0.01602],"object_pos_start":[0.46687,0.04204,0.01602],"object_to_goal_dist_end":0.24391,"object_to_goal_dist_start":0.24391,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47461,0.04115,0.19414],"tcp_start":[0.50948,0.0603,0.34916],"tcp_to_object_dist_end":0.17829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":78.0,"average_failure_rate":0.29658,"average_mean_iterations":63.25475,"average_solve_count":263.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.08859,"approach_pre_grasp.speed":0.04031,"descend_place.speed":0.04427,"descend_to_grasp.force_threshold":8.48075,"descend_to_grasp.speed":0.02164,"grasp.grasp_duration":0.70944,"lift.lift_height":0.10188,"lift.speed":0.05522,"release.release_duration":0.27129,"retract.speed":0.09668},"optimized_scores":{"best_composite_score":-0.39486,"best_fitness_score":0.16014,"best_task_score":0.12361},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":883.0,"contact_point_centroid":[0.62749,0.03019,-0.00045],"force_p95":217.48343,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1441.83859,"mean_force":213.22133,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38755,0.02887,0.12738]},{"body_a":"link5","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.53603,0.06862,0.22474],"force_p95":361.46943,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.56856,"mean_force":312.7342,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50367,0.15964,0.24467]},{"body_a":"link5","body_b":"hand","contact_count":517.0,"contact_point_centroid":[0.53628,0.14984,0.16423],"force_p95":136.84582,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.91713,"mean_force":95.36111,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47254,0.06975,0.12637]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.62207,0.0392,-0.00011],"force_p95":199.492,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.96959,"mean_force":144.93029,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.39278,0.04089,0.14817]},{"body_a":"link5","body_b":"hand","contact_count":24.0,"contact_point_centroid":[0.51625,0.11308,0.16543],"force_p95":150.54955,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.82772,"mean_force":116.74677,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48639,0.02209,0.10723]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.52557,0.11036,0.17935],"force_p95":118.45284,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.5868,"mean_force":100.0777,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48096,0.02136,0.12151]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.621,0.03937,-0.00026],"force_p95":107.33971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.33971,"mean_force":107.33971,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39212,0.04098,0.1485]},{"body_a":"link5","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.52421,0.1117,0.17577],"force_p95":86.59323,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.47963,"mean_force":69.70374,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.47941,0.02269,0.11822]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62181,0.03918,-0.00014],"force_p95":83.39614,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.53615,"mean_force":72.62341,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39254,0.04078,0.14813]},{"body_a":"grasp_target","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.4825,0.02819,0.01877],"force_p95":2.78852,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.62294,"mean_force":0.69932,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37445,0.01984,0.07448]},{"body_a":"grasp_target","body_b":"hand","contact_count":70.0,"contact_point_centroid":[0.46181,0.04365,0.04784],"force_p95":3.2751,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.51436,"mean_force":1.11123,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37938,0.01998,0.07808]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.44533,0.05047,-0.00221],"force_p95":0.22962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09096,"mean_force":0.1444,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.4008,0.02754,0.13764]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43819,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39212,0.04098,0.1485]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43819,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39254,0.04078,0.14813]},{"body_a":"world","body_b":"grasp_target","contact_count":2712.0,"contact_point_centroid":[0.43819,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45323,0.10389,0.2016]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43819,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47792,0.09976,0.15707]}],"total_contact_groups":25},"final_pose_error":0.06517,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.43819,0.05081,0.01602],"final_tcp_position":[0.46945,-0.00244,0.14517],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":272983.8929,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":217.10734,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4788.0,"raw_peak_contact_force":1441.83859,"subtask_id":"approach_object","tcp_end":[0.39212,0.04098,0.1485],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14061,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":107.33971,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":107.33971,"subtask_id":"grasp_object","tcp_end":[0.39212,0.04093,0.14849],"tcp_start":[0.39212,0.04098,0.1485],"tcp_to_object_dist_end":0.1406,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":69.14569,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3511.0,"raw_peak_contact_force":87.53615,"tcp_end":[0.39262,0.04074,0.14798],"tcp_start":[0.39262,0.04075,0.14798],"tcp_to_object_dist_end":0.13997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":260.95125,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5700.0,"raw_peak_contact_force":382.56856,"subtask_id":"lift_object","tcp_end":[0.51273,0.169,0.24974],"tcp_start":[0.51224,0.1691,0.249],"tcp_to_object_dist_end":0.27231,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":272983.8929,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8818.0,"raw_peak_contact_force":328.91713,"tcp_end":[0.48627,0.02204,0.10715],"tcp_start":[0.51273,0.169,0.24974],"tcp_to_object_dist_end":0.10698,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8330.0,"raw_peak_contact_force":152.82772,"subtask_id":"place_at_goal","tcp_end":[0.48007,0.02501,0.10057],"tcp_start":[0.48627,0.02204,0.10715],"tcp_to_object_dist_end":0.09782,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":66.57457,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1070.0,"raw_peak_contact_force":92.47963,"tcp_end":[0.481,0.0214,0.1216],"tcp_start":[0.48007,0.02501,0.10057],"tcp_to_object_dist_end":0.11766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.43819,0.05081,0.01602],"object_pos_start":[0.43819,0.05081,0.01602],"object_to_goal_dist_end":0.31359,"object_to_goal_dist_start":0.31359,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1711.0,"raw_peak_contact_force":118.5868,"tcp_end":[0.46945,-0.00244,0.14517],"tcp_start":[0.481,0.0214,0.1216],"tcp_to_object_dist_end":0.14315,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":212.0,"average_failure_rate":0.57609,"average_mean_iterations":117.70652,"average_solve_count":368.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.14224,"approach_pre_grasp.speed":0.02861,"descend_place.speed":0.02631,"descend_to_grasp.force_threshold":5.00154,"descend_to_grasp.speed":0.03111,"grasp.grasp_duration":1.29727,"lift.lift_height":0.07831,"lift.speed":0.01875,"release.release_duration":0.57636,"retract.speed":0.07718},"optimized_scores":{"best_composite_score":-0.42978,"best_fitness_score":0.12522,"best_task_score":0.10496},"replay_outcomes":[{"contacts":{"omitted_contact_groups":16,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":882.0,"contact_point_centroid":[0.62876,0.03206,-0.00049],"force_p95":216.37569,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1574.37787,"mean_force":212.53969,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39425,0.03116,0.13682]},{"body_a":"link5","body_b":"hand","contact_count":72.0,"contact_point_centroid":[0.52882,0.05235,0.18624],"force_p95":486.72863,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.17552,"mean_force":392.56327,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49611,0.13883,0.20552]},{"body_a":"world","body_b":"link6","contact_count":285.0,"contact_point_centroid":[0.66079,-0.05732,-0.00031],"force_p95":270.53091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.89594,"mean_force":206.31548,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53129,0.03658,0.21714]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.62214,0.04113,-0.00011],"force_p95":353.60537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.5034,"mean_force":230.33361,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4026,0.04422,0.16221]},{"body_a":"link5","body_b":"hand","contact_count":679.0,"contact_point_centroid":[0.52357,-0.00636,0.15358],"force_p95":320.13037,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.23992,"mean_force":288.94995,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52028,0.06543,0.20541]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.52638,-0.03037,0.15586],"force_p95":319.06155,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.03536,"mean_force":282.47351,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5386,0.01255,0.23369]},{"body_a":"link5","body_b":"hand","contact_count":327.0,"contact_point_centroid":[0.5245,-0.04234,0.16905],"force_p95":237.14142,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.85761,"mean_force":124.73977,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52797,-0.00061,0.24625]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52813,-0.0293,0.16236],"force_p95":279.99831,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.05965,"mean_force":250.03019,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53918,0.01332,0.2406]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.66068,-0.06124,-0.00025],"force_p95":217.82242,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.60901,"mean_force":190.80591,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5386,0.01255,0.23369]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.66087,-0.06084,-8e-05],"force_p95":67.55781,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.47339,"mean_force":52.27221,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53875,0.0132,0.23393]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62108,0.04134,-0.00025],"force_p95":98.07981,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.07981,"mean_force":98.07981,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40194,0.04432,0.16246]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.65457,-0.10846,-0.0002],"force_p95":94.46172,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.86541,"mean_force":63.71733,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52639,-0.01091,0.21802]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62189,0.04108,-0.00014],"force_p95":80.64874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.66236,"mean_force":72.8469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.40233,0.0441,0.16213]},{"body_a":"grasp_target","body_b":"link6","contact_count":75.0,"contact_point_centroid":[0.53126,-0.0003,0.02398],"force_p95":1.01427,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.0014,"mean_force":0.48755,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38047,0.02179,0.09127]},{"body_a":"grasp_target","body_b":"link7","contact_count":135.0,"contact_point_centroid":[0.49773,-0.01813,0.04474],"force_p95":2.75943,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.7651,"mean_force":0.79109,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38563,0.02216,0.09721]},{"body_a":"grasp_target","body_b":"hand","contact_count":109.0,"contact_point_centroid":[0.49035,-0.02777,0.0486],"force_p95":2.16341,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.06887,"mean_force":0.85179,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38423,0.02194,0.09283]}],"total_contact_groups":32},"final_pose_error":0.06341,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49295,-0.02509,0.01602],"final_tcp_position":[0.52654,-0.0108,0.21787],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1574.37787,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.31446,"object_z_max":0.03006,"peak_contact_force":215.95945,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4906.0,"raw_peak_contact_force":1574.37787,"subtask_id":"approach_object","tcp_end":[0.40194,0.04432,0.16246],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18586,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":98.07981,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":98.07981,"subtask_id":"grasp_object","tcp_end":[0.40195,0.04428,0.16244],"tcp_start":[0.40194,0.04432,0.16246],"tcp_to_object_dist_end":0.18583,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":70.01434,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3505.0,"raw_peak_contact_force":83.66236,"tcp_end":[0.4024,0.04405,0.162],"tcp_start":[0.4024,0.04406,0.162],"tcp_to_object_dist_end":0.18518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":311.88853,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4076.0,"raw_peak_contact_force":516.17552,"subtask_id":"lift_object","tcp_end":[0.50429,0.14627,0.20858],"tcp_start":[0.50381,0.14594,0.20821],"tcp_to_object_dist_end":0.25802,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":312.04121,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6643.0,"raw_peak_contact_force":357.89594,"tcp_end":[0.5386,0.01254,0.23362],"tcp_start":[0.50429,0.14627,0.20858],"tcp_to_object_dist_end":0.22549,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":318.5202,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":51.0,"raw_peak_contact_force":321.03536,"subtask_id":"place_at_goal","tcp_end":[0.53861,0.01276,0.23376],"tcp_start":[0.5386,0.01254,0.23362],"tcp_to_object_dist_end":0.22567,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":264.79641,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1350.0,"raw_peak_contact_force":282.05965,"tcp_end":[0.54011,0.01363,0.26141],"tcp_start":[0.53861,0.01276,0.23376],"tcp_to_object_dist_end":0.25287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":658.0,"n_steps_budget":930.0,"object_pos_end":[0.49295,-0.02509,0.01602],"object_pos_start":[0.49295,-0.02509,0.01602],"object_to_goal_dist_end":0.33813,"object_to_goal_dist_start":0.33813,"object_z_max":0.01602,"peak_contact_force":97.86541,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4571.0,"raw_peak_contact_force":291.85761,"tcp_end":[0.52654,-0.0108,0.21787],"tcp_start":[0.54011,0.01363,0.26141],"tcp_to_object_dist_end":0.20512,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```